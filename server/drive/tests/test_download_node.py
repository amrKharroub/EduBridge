import pytest
from django.urls import reverse
from rest_framework import status
from drive.models import Node, NodeVersion, ZipFolder
import hashlib
import uuid
import time

def upload_dummy_blob(container, storage_key: str, content: bytes):
    blob_client = container.get_blob_client(storage_key)
    blob_client.upload_blob(
        content,
        overwrite=True,
    )

def fake_checksum(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def fake_storage_key(user_id: int, name: str) -> str:
    return f"users/{user_id}/{uuid.uuid4()}-{name}"

def assert_download_file_response(data, expected_filename):
    assert data["status"] == "done"
    assert data["filename"] == expected_filename
    assert "download_url" in data
    assert data["download_url"].startswith("http")


def assert_zip_task_response(data):
    assert data["status"] == "Zipping files"
    assert "task_id" in data

def create_blob_and_version(
    *,
    container,
    node,
    content: bytes,
    mime_type: str,
):
    storage_key = fake_storage_key(node.owner.id, node.name)

    upload_dummy_blob(
        container=container,
        storage_key=storage_key,
        content=content,
    )

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

def create_file_node(
    *,
    parent,
    owner,
    name: str,
    status,
    container,
    content: bytes,
    mime_type="application/octet-stream",
):
    file_node = parent.add_child(
        name=name,
        owner=owner,
        type=Node.NodeType.file,
        status=status,
    )

    create_blob_and_version(
        container=container,
        node=file_node,
        content=content,
        mime_type=mime_type,
    )

    return file_node

@pytest.fixture
def file_node_with_blob(create_container, user, root_folder):
    """
    Folder structure:

    Project Docs/
    ├── file1.txt        (ACTIVE)
    ├── file2.txt        (TRASHED)
    └── child_folder/
        ├── file3.txt    (ACTIVE)
        └── file4.txt    (TRASHED)
    """
    parent = root_folder.add_child(
        name="Project Docs first",
        owner=user,
        type=Node.NodeType.folder,
        status=Node.NodeStatus.ACTIVE,
    )

    create_file_node(
        parent=parent,
        owner=user,
        name="file1.txt",
        status=Node.NodeStatus.ACTIVE,
        container=create_container,
        content=b"primary content",
        mime_type="text/plain",
    )

    create_file_node(
        parent=parent,
        owner=user,
        name="file2.txt",
        status=Node.NodeStatus.TRASHED,
        container=create_container,
        content=b"secondary content",
        mime_type="text/plain",
    )

    child_folder = parent.add_child(
        name="child_folder",
        owner=user,
        type=Node.NodeType.folder,
        status=Node.NodeStatus.ACTIVE,
    )

    create_file_node(
        parent=child_folder,
        owner=user,
        name="file3.txt",
        status=Node.NodeStatus.ACTIVE,
        container=create_container,
        content=b"large content" * 1024,
        mime_type="application/octet-stream",
    )

    create_file_node(
        parent=child_folder,
        owner=user,
        name="file4.txt",
        status=Node.NodeStatus.TRASHED,
        container=create_container,
        content=b"small content" * 20,
        mime_type="application/octet-stream",
    )

    return parent

@pytest.mark.django_db
def test_download_file_node_returns_direct_download(
    user,
    api_client,
    create_container,
    root_folder,
):
    content = b"dummy file content"
    storage_key = fake_storage_key(user.id, "file.txt")

    upload_dummy_blob(create_container, storage_key, content)

    file_node = root_folder.add_child(
        name="file.txt",
        owner=user,
        type=Node.NodeType.file,
        status=Node.NodeStatus.ACTIVE,
    )

    version = NodeVersion.objects.create(
        node=file_node,
        storage_key=storage_key,
        size=len(content),
        mime_type="text/plain",
        checksum=fake_checksum(content),
        status=NodeVersion.FileStatus.ACTIVE,
    )

    file_node.current_version = version
    file_node.save()

    api_client.force_authenticate(user)
    url = reverse("download-node", args=[file_node.id])

    response = api_client.get(url)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert_download_file_response(response.data, expected_filename="file.txt")

@pytest.fixture(autouse=True)
def celery_eager(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    
@pytest.mark.django_db
def test_download_folder_node_creates_zip_task(
    user,
    api_client,
    file_node_with_blob,
):
    folder = file_node_with_blob

    api_client.force_authenticate(user)
    url = reverse("download-node", args=[folder.id])

    response = api_client.get(url)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert_zip_task_response(response.data)
    
    zip_folder = ZipFolder.objects.get(node=folder.id)
    task_id = response.data["task_id"]
    polling_url = reverse("task-status", args=[task_id])

    # Poll with timeout protection
    for _ in range(10):
        task_response = api_client.get(polling_url)
        data = task_response.data

        assert "status" in data
        assert "ready" in data
        assert "successful" in data

        if data["status"] == "SUCCESS":
            zip_folder.refresh_from_db()
            assert data["ready"] is True
            assert data["successful"] is True
            assert "download_url" in data["result"]
            assert ZipFolder.objects.count() == 1
            assert zip_folder.status == ZipFolder.ZipFolderStatus.COMPLETED
            break
        time.sleep(0.5)

    else:
        pytest.fail("Zip task did not complete within expected time")


@pytest.mark.django_db
def test_cannot_download_trashed_node(user, api_client, root_folder):
    trashed_file = root_folder.add_child(
        name="old.txt",
        owner=user,
        type=Node.NodeType.file,
        status=Node.NodeStatus.TRASHED,
    )

    api_client.force_authenticate(user)
    url = reverse("download-node", args=[trashed_file.id])

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND

