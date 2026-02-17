import hashlib
from azure.storage.blob import BlobClient
import base64
import pytest
from django.urls import reverse
from django.conf import settings
from azure.storage.blob import ContentSettings
from drive.models import StorageUsage

@pytest.mark.django_db
def test_initialize_and_finalize_file_upload(
    api_client,
    user,
):
    api_client.force_authenticate(user=user)

    file_content = b"Hello Azurite!"
    filename = "hello.txt"
    mime_type = "text/plain"
    size = len(file_content)
    checksum = hashlib.md5(file_content).hexdigest()

    # --------------------
    # 1. INIT UPLOAD
    # --------------------
    init_url = reverse("init-upload")  # your DRF route
    
    init_payload = {
        "filename": filename,
        "size": size,
        "mime_type": mime_type,
        "checksum": checksum,
        "parent_id": None,
    }

    init_response = api_client.post(init_url, init_payload, format="json")
    assert init_response.status_code == 200

    upload_url = init_response.data["upload_url"]
    version_id = init_response.data["version_id"]
    node_id = init_response.data["node_id"]

    # --------------------
    # 2. DIRECT UPLOAD TO AZURITE (REAL UPLOAD)
    # --------------------
    blob_client = BlobClient.from_blob_url(upload_url)

    blob_client.upload_blob(
        file_content,
        overwrite=True,
        content_settings=ContentSettings(
            content_type=mime_type
        )
    )

    # --------------------
    # 3. FINALIZE UPLOAD
    # --------------------
    finalize_url = reverse("finalize-upload", kwargs={"node_id": node_id})
    finalize_payload = {
        "version_id": version_id
    }

    finalize_response = api_client.post(
        finalize_url, finalize_payload, format="json"
    )

    assert finalize_response.status_code == 201

    data = finalize_response.data
    usage = StorageUsage.objects.get(user=user)
    assert usage.used_bytes == size
    assert data["filename"] == filename
    assert data["mime_type"] == mime_type


@pytest.mark.django_db
def test_initialize_and_finalize_file_upload_multipart(
    api_client,
    user,
):
    api_client.force_authenticate(user=user)

    # Make content big enough to justify chunking
    file_content = b"Hello Azurite! " * 1024  # ~14 KB
    filename = "hello_multipart.txt"
    mime_type = "text/plain"
    size = len(file_content)
    checksum = hashlib.md5(file_content).hexdigest()

    # --------------------
    # 1. INIT UPLOAD
    # --------------------
    init_url = reverse("init-upload")
    init_payload = {
        "filename": filename,
        "size": size,
        "mime_type": mime_type,
        "checksum": checksum,
        "parent_id": None,
    }

    init_response = api_client.post(init_url, init_payload, format="json")
    assert init_response.status_code == 200

    upload_url = init_response.data["upload_url"]
    version_id = init_response.data["version_id"]
    node_id = init_response.data["node_id"]

    blob_client = BlobClient.from_blob_url(upload_url)

    # --------------------
    # 2. MULTI-PART (BLOCK) UPLOAD
    # --------------------
    chunk_size = 4 * 1024  # 4 KB blocks
    block_ids = []

    for index, offset in enumerate(range(0, size, chunk_size)):
        chunk = file_content[offset : offset + chunk_size]

        # Azure requires base64-encoded block IDs
        block_id = base64.b64encode(f"block-{index:06d}".encode()).decode()
        block_ids.append(block_id)

        blob_client.stage_block(
            block_id=block_id,
            data=chunk,
        )

    # Commit blocks + set metadata
    blob_client.commit_block_list(
        block_ids,
        content_settings=ContentSettings(
            content_type=mime_type
        ),
    )

    # --------------------
    # 3. FINALIZE UPLOAD
    # --------------------
    finalize_url = reverse("finalize-upload", kwargs={"node_id": node_id})
    finalize_payload = {
        "version_id": version_id
    }

    finalize_response = api_client.post(
        finalize_url, finalize_payload, format="json"
    )

    assert finalize_response.status_code == 201

    data = finalize_response.data
    usage = StorageUsage.objects.get(user=user)

    assert usage.used_bytes == size
    assert data["filename"] == filename
    assert data["mime_type"] == mime_type
