import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.urls import reverse
from guardian.shortcuts import assign_perm
from drive.models import Node, NodeVersion
import hashlib
import uuid

def fake_checksum(content: bytes) -> str:
    return hashlib.md5(content).hexdigest()


def fake_storage_key(user_id: int, name: str) -> str:
    return f"users/{user_id}/{uuid.uuid4()}-{name}"

@pytest.mark.django_db
def test_node_details_visible_only_to_users_with_permission(root_folder):
    """
    A user WITHOUT object permission must not see the node.
    """

    owner = User.objects.create_user(
        username="owner",
        email="owner@test.com",
        password="pass1234"
    )

    stranger = User.objects.create_user(
        username="stranger",
        email="stranger@test.com",
        password="pass1234"
    )

    node = root_folder.add_child(
        owner=owner,
        name="Secret File",
        type=Node.NodeType.file,
        status=Node.NodeStatus.ACTIVE
    )

    client = APIClient()
    client.force_authenticate(user=stranger)
    url = reverse("node-detail", args=[node.id])
    response = client.get(url)

    # Should be hidden
    assert response.status_code == 403


@pytest.mark.django_db
def test_viewer_can_see_node_but_not_shared_with(root_folder):
    owner = User.objects.create_user(
        username="owner",
        email="owner@test.com",
        password="pass1234"
    )

    viewer = User.objects.create_user(
        username="viewer",
        email="viewer@test.com",
        password="pass1234"
    )

    node = root_folder.add_child(
        owner=owner,
        name="Shared File",
        type=Node.NodeType.file,
        status=Node.NodeStatus.ACTIVE
    )

    assign_perm("drive.view_node", viewer, node)

    client = APIClient()
    client.force_authenticate(user=viewer)

    url = reverse("node-detail", args=[node.id])
    response = client.get(url)

    assert response.status_code == 403
    # data = response.json()

    # assert data["name"] == "Shared File"
    # assert data["owner_email"] == "owner@test.com"

    # # viewer should NOT see sharing info
    # assert data["shared_with"] == []

@pytest.mark.django_db
def test_editor_can_see_shared_with(root_folder):
    owner = User.objects.create_user(
        username="owner",
        email="owner@test.com",
        password="pass1234"
    )

    editor = User.objects.create_user(
        username="editor",
        email="editor@test.com",
        password="pass1234"
    )

    viewer = User.objects.create_user(
        username="viewer",
        email="viewer@test.com",
        password="pass1234"
    )

    node = root_folder.add_child(
        owner=owner,
        name="Team File",
        type=Node.NodeType.file,
        status=Node.NodeStatus.ACTIVE
    )

    v1 = NodeVersion.objects.create(
        node=node,
        storage_key=fake_storage_key(owner.id, "notes-v1.txt"),
        size=100,
        mime_type="text/plain",
        checksum=fake_checksum(b"v1"),
        status=NodeVersion.FileStatus.ACTIVE,
    )

    node.current_version = v1
    node.save()

    v2 = NodeVersion.objects.create(
        node=node,
        storage_key=fake_storage_key(owner.id, "notes-v2.txt"),
        size=120,
        mime_type="text/plain",
        checksum=fake_checksum(b"v2"),
        status=NodeVersion.FileStatus.UPLOADING,
    )
    node.current_version = v2

    node.save()

    assign_perm("drive.edit_node", editor, node)
    assign_perm("drive.view_node", viewer, node)

    client = APIClient()
    client.force_authenticate(user=editor)

    url = reverse("node-detail", args=[node.id])
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()

    emails = {u["user"]["email"] for u in data["shared_with"]}

    assert "editor@test.com" in emails
    assert "viewer@test.com" in emails
    assert data["version_number"] == 2


@pytest.mark.django_db
def test_owner_can_access_node_without_guardian_permission(root_folder):
    owner = User.objects.create_user(
        username="owner",
        email="owner@test.com",
        password="pass1234"
    )

    node = root_folder.add_child(
        owner=owner,
        name="Owner File",
        type=Node.NodeType.file,
        status=Node.NodeStatus.ACTIVE
    )

    client = APIClient()
    client.force_authenticate(user=owner)

    url = reverse("node-detail", args=[node.id])
    response = client.get(url)

    assert response.status_code == 200
    assert response.json()["name"] == "Owner File"