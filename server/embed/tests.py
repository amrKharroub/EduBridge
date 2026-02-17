import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from drive.models import Node, NodeVersion
from embed.models import NodeVectorUsage, VectorStorageUsage
from django.contrib.auth.models import User
import hashlib
import uuid
from embed.tasks import update_vectorisation_telemetry
from drive.core.services.redis_cache import redis_client, VECTOR_STATUS_KEY
import time

@pytest.fixture
def user():
    return User.objects.create_user(
        username="alice",
        email="alice@test.com",
        password="StrongPass123!"
    )

@pytest.fixture
def root_folder(user):
    """
    Root folder for a user
    """
    return Node.add_root(
        owner=user,
        name="root",
        type=Node.NodeType.folder,
        status=Node.NodeStatus.ACTIVE,
    )

@pytest.fixture
def node(user, root_folder):
    return root_folder.add_child(
        name="Project Docs",
        owner=user,
        type=Node.NodeType.file,
        status=Node.NodeStatus.ACTIVE,
    )

@pytest.fixture
def api_client():
    return APIClient()

def fake_checksum(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def fake_storage_key(user_id: int, name: str) -> str:
    return f"users/{user_id}/{uuid.uuid4()}-{name}"

def create_blob_version(
    node,
    content: bytes,
    mime_type: str,
):
    storage_key = fake_storage_key(node.owner.id, node.name)

    version = NodeVersion.objects.create(
        node=node,
        storage_key=storage_key,
        size=len(content),
        mime_type=mime_type,
        checksum=fake_checksum(content),
        status=NodeVersion.FileStatus.ACTIVE,
    )

    node.current_version = version
    node.save()
    return version

@pytest.mark.django_db
def test_vectorisation_job(node, user, api_client):
    create_blob_version(node, b"Hello World again!", 'application/pdf')
    api_client.force_authenticate(user)
    url = reverse("generate-embedding", args=[node.id])

    response = api_client.post(url)
    task_id = response.data["job_id"]
    assert response.status_code == status.HTTP_202_ACCEPTED
    count = 0
    while(True):
        if count >= 5:
            assert False # took too long
        task_status = redis_client.get(f"{VECTOR_STATUS_KEY}:{task_id}")
        if task_status != "initializing":
            assert task_status == "pending-vectorising"
            break
        count += 1
        time.sleep(5)


@pytest.mark.django_db
def test_update_telemetry_job(node, user):
    version = create_blob_version(node, b"Hello World again!", 'application/pdf')
    tel = [{'vector_count': 2, 'text_size': 1886, 'user_id': user.id, 'document_id': node.id, 'version_number': version.version_number, 'vector_size': 384, 'increment': True}]
    update_vectorisation_telemetry.delay(tel, 1)

    status = redis_client.get(f"{VECTOR_STATUS_KEY}:1")
    assert status == "success"

    node_embed_info = NodeVectorUsage.objects.filter(document_id=node.id).first()
    assert node_embed_info is not None
    assert node_embed_info.owner == user
    assert node_embed_info.version_number == version.version_number
    assert node_embed_info.vector_count == 2
    assert node_embed_info.text_size == 1886
    assert node_embed_info.total_usage == 2 * 384 * 4 * 1.5 + 1886

    storage_usage = VectorStorageUsage.objects.filter(user_id =user.id).first()
    assert storage_usage is not None
    assert storage_usage.used_bytes == 2 * 384 * 4 * 1.5 + 1886


@pytest.mark.django_db
def test_replace_vectorise_job(node, user, api_client):
    create_blob_version(node, b"Hello World again!", 'application/pdf')
    NodeVectorUsage.objects.create(
        document=node,
        owner=user
    )
    api_client.force_authenticate(user)
    url = reverse("generate-embedding", args=[node.id])

    response = api_client.post(url)
    task_id = response.data["job_id"]
    assert response.status_code == status.HTTP_202_ACCEPTED
    count = 0
    while(True):
        if count >= 5:
            assert False # taking too long
        task_status = redis_client.get(f"{VECTOR_STATUS_KEY}:{task_id}")
        if task_status != "initializing":
            assert task_status == "pending-vectorising" or task_status == "pending-replacing" or task_status == "pending-deleting"
            break
        count += 1
        time.sleep(5)