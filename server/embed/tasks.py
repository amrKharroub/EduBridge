# embed/tasks.py
from embed.models import VectorStorageUsage, NodeVectorUsage
from celery import shared_task, chain
from django.db import transaction
from django.shortcuts import get_object_or_404
from drive.models import Node
from django.contrib.auth.models import User
from drive.core.services.redis_cache import redis_client, VECTOR_STATUS_KEY
from llama_cloud import LlamaCloud
from llama_cloud.types.parsing_get_response import ParsingGetResponse
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from qdrant_client import models, QdrantClient
import uuid



def decrement_usage(data):
    doc_usage = NodeVectorUsage.objects.get(document_id=data["document_id"])
    user_usage = VectorStorageUsage.objects.get(user_id=data["user_id"])
    user_usage.used_bytes -= doc_usage.total_usage
    user_usage.save()
    doc_usage.delete()

def increment_usage(data):
    node = get_object_or_404(Node.active_objects, pk=data["document_id"])
    owner = get_object_or_404(User, pk=data["user_id"])
    node_usage = NodeVectorUsage.objects.create(
        document=node,
        owner=owner,
        version_number=data["version_number"],
        vector_count=data["vector_count"],
        text_size=data["text_size"]
    )
    vector_usage, _ = VectorStorageUsage.objects.get_or_create(user=owner)

    used_bytes = (
        data["vector_count"] * data["vector_size"] * 4 * 1.5 +
        data["text_size"]
    )

    vector_usage.used_bytes += used_bytes
    node_usage.total_usage = used_bytes

    with transaction.atomic():
        vector_usage.save()
        node_usage.save()


@shared_task(name="embed.update_vectorisation_telemetry")
def update_vectorisation_telemetry(usage_telemetry, task_id):
    redis_client.set(f"{VECTOR_STATUS_KEY}:{task_id}", "pending-updatingTelemetry", keepttl=True)
    try:
        for usage in usage_telemetry:
            if usage["increment"]:
                increment_usage(usage)
            else:
                decrement_usage(usage)
    except Exception as e:
        redis_client.set(f"{VECTOR_STATUS_KEY}:{task_id}", f"failed-{e}", keepttl=True)
        return
    redis_client.set(f"{VECTOR_STATUS_KEY}:{task_id}", "success", keepttl=True)


def parse_file(client: LlamaCloud, **kwargs):
    valid_keys = {'file_id', 'source_url', 'upload_file'}
    present_keys = valid_keys.intersection(kwargs.keys())
    if not present_keys:
        raise ValueError(
            "At least one of the following keys must be provided: "
            "file_id, source_url, upload_file"
        )
    kwargs_copy = kwargs.copy()

    if 'file_id' in kwargs_copy:
        kwargs_copy.pop('source_url', None)
        kwargs_copy.pop('upload_file', None)
    elif 'source_url' in kwargs_copy:
        kwargs_copy.pop('upload_file', None)

    default_config = {
        "tier": "agentic",
        "version": "latest",
        "output_options": {
            "markdown": {
                "annotate_links": True,
                "tables": {
                    "compact_markdown_tables": True,
                    "output_tables_as_markdown": True,
                }
            },
        },
        "expand": ["markdown", "items"]
    }
    config = default_config.copy()
    for key, value in kwargs_copy.items():
        config[key] = value

    return client.parsing.parse(**config)

def process_content(result: ParsingGetResponse, doc_metadata: dict):
    headers_to_split_on = [
        ("#", "Header_1"),
        ("##", "Header_2"),
        ("###", "Header_3"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False
    )
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    final_documents = []
    for i, page in enumerate(result.markdown.pages):
        cur_page = i + 1
        page_text = page.markdown
        header_splits = markdown_splitter.split_text(page_text)

        for split in header_splits:
            metadata = {
                **doc_metadata,
                "page_number": cur_page,
                **split.metadata
            }
            sub_docs = text_splitter.split_documents([
                Document(page_content=split.page_content, metadata=metadata)
            ])
            final_documents.extend(sub_docs)
    return final_documents

def store_content(client: QdrantClient, collection_name: str, model_name: str, content: list):
    usage_telemetry = {
        "vector_count": 0,
        "text_size": 0
    }
    metadata_with_docs = [
        {"document_chunk": doc.page_content, **doc.metadata} for doc in content
    ]
    usage_telemetry["text_size"] = sum(
        len(bytes(doc["document_chunk"], encoding="utf-8")) for doc in metadata_with_docs
    )
    usage_telemetry["vector_count"] = len(metadata_with_docs)
    ids = [str(uuid.uuid4()) for _ in range(len(content))]
    client.upload_collection(
        collection_name=collection_name,
        vectors=[models.Document(text=doc.page_content, model=model_name) for doc in content],
        payload=metadata_with_docs,
        ids=ids
    )
    return usage_telemetry

@shared_task(name="embed.vectorise_file")
def vectorise_file(prev_tel, props, update_tel=False):
    """
    Vectorise a file based on props. Appends telemetry to prev_tel and returns the updated list.
    If update_tel is True, triggers the telemetry update task.
    """
    redis_client.set(f"{VECTOR_STATUS_KEY}:{props['task_id']}", "pending-vectorising", keepttl=True)

    llama_client = LlamaCloud(api_key=props["llama_cloud_key"])
    client = QdrantClient(props["connection_url"])

    collection_name = props["collection_name"]
    model_name = props["model_name"]
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=client.get_embedding_size(model_name),
                distance=models.Distance.COSINE
            )
        )
        client.create_payload_index(
            collection_name=collection_name,
            field_name="user_id",
            field_schema=models.PayloadSchemaType.INTEGER
        )
        client.create_payload_index(
            collection_name=collection_name,
            field_name="document_id",
            field_schema=models.PayloadSchemaType.INTEGER
        )

    result = parse_file(llama_client, **props["parse_settings"])
    documents = process_content(result, props["doc_metadata"])
    usage_telemetry = store_content(client, collection_name, model_name, documents)

    # Enrich telemetry with metadata
    usage_telemetry["user_id"] = props["doc_metadata"]["user_id"]
    usage_telemetry["document_id"] = props["doc_metadata"]["document_id"]
    usage_telemetry["version_number"] = props["doc_metadata"]["version_number"]
    usage_telemetry["vector_size"] = client.get_embedding_size(model_name)
    usage_telemetry["increment"] = True

    prev_tel.append(usage_telemetry)

    if update_tel:
        update_vectorisation_telemetry.delay(prev_tel, props["task_id"])

    return prev_tel


@shared_task(name="embed.delete_document")
def delete_document(prev_tel, props, update_tel=False):
    """
    Delete all vectors belonging to the document from Qdrant.
    Appends a deletion telemetry record to prev_tel and returns the updated list.
    If update_tel is True, triggers the telemetry update task.
    """
    redis_client.set(f"{VECTOR_STATUS_KEY}:{props['task_id']}", "pending-deleting", keepttl=True)

    client = QdrantClient(props["connection_url"])
    collection_name = props["collection_name"]

    if not client.collection_exists(collection_name):
        raise ValueError("Collection does not exist")

    client.delete(
        collection_name=collection_name,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=props["doc_metadata"]["document_id"]),
                    ),
                ],
            )
        ),
    )

    usage_telemetry = {
        "increment": False,
        "document_id": props["doc_metadata"]["document_id"],
        "user_id": props["doc_metadata"]["user_id"]
    }
    prev_tel.append(usage_telemetry)

    if update_tel:
        update_vectorisation_telemetry.delay(prev_tel, props["task_id"])

    return prev_tel


@shared_task(name="embed.replace_document")
def replace_document(props):
    """
    Replace a document by first deleting its old vectors and then vectorising the new file.
    Returns the ID of the final task in the workflow.
    """
    redis_client.set(f"{VECTOR_STATUS_KEY}:{props['task_id']}", "pending-replacing", keepttl=True)

    workflow = chain(
        delete_document.s([], props, False),
        vectorise_file.s(props, True)
    )

    result = workflow.delay()
    return str(result.id)