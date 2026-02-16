import pytest
from django.urls import reverse
from django.contrib.auth.models import User

from drive.models import Node
from guardian.models import UserObjectPermission


@pytest.mark.django_db
def test_owner_can_share_node_with_multiple_users(user, api_client, root_folder):
    api_client.force_authenticate(user=user)

    node = root_folder.add_child(
        name="Project Docs",
        owner=user,
        type=Node.NodeType.file,
        status=Node.NodeStatus.ACTIVE,
    )
    alice1 = User.objects.create_user(
        username="neo_alice",
        email="alice@example.com",
        password="StrongPass123!"
    )
    bob = User.objects.create_user(
        username="bob",
        email="bob@example.com",
        password="StrongPass123!"
    )

    url = reverse("node-share", args=[node.id])
    payload = {
        "emails": [
            "alice@example.com",
            "bob@example.com",
        ],
        "access_level": "viewer",
    }

    response = api_client.post(url, payload, format="json")

    assert response.status_code == 201
    assert alice1.has_perm("drive.view_node", node)
    assert bob.has_perm("drive.view_node", node)

    assert not alice1.has_perm("drive.add_node", node)
    assert not bob.has_perm("drive.change_node", node)


@pytest.mark.django_db
def test_invalid_access_level_returns_400(user, api_client, root_folder):
    api_client.force_authenticate(user=user)

    node = root_folder.add_child(
        name="Project Docs",
        owner=user,
        type=Node.NodeType.file,
        status=Node.NodeStatus.ACTIVE,
    )
    User.objects.create_user(
        username="neo_alice",
        email="alice@example.com",
        password="StrongPass123!"
    )

    url = reverse("node-share", args=[node.id])
    payload = {
        "emails": ["alice@example.com"],
        "access_level": "admin",  # invalid
    }

    response = api_client.post(url, payload, format="json")

    assert response.status_code == 400
    assert "access_level" in response.data


@pytest.mark.django_db
def test_unauthenticated_user_cannot_share(user, api_client, root_folder):
    node = root_folder.add_child(
        name="Project Docs",
        owner=user,
        type=Node.NodeType.file,
        status=Node.NodeStatus.ACTIVE,
    )

    url = reverse("node-share", args=[node.id])
    payload = {
        "emails": ["alice@example.com"],
        "access_level": "viewer",
    }

    response = api_client.post(url, payload, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_user_without_permission_cannot_share(user, api_client, root_folder):
    stranger = User.objects.create_user(
        username="stranger",
        email="stranger@example.com",
        password="StrongPass123!"
    )

    node = root_folder.add_child(
        name="Project Docs",
        owner=user,
        type=Node.NodeType.file,
        status=Node.NodeStatus.ACTIVE,
    )

    api_client.force_authenticate(user=stranger)

    url = reverse("node-share", args=[node.id])
    payload = {
        "emails": ["alice@example.com"],
        "access_level": "viewer",
    }

    response = api_client.post(url, payload, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_duplicate_emails_are_rejected(user, api_client, root_folder):
    api_client.force_authenticate(user=user)

    node = root_folder.add_child(
        name="Project Docs",
        owner=user,
        type=Node.NodeType.file,
        status=Node.NodeStatus.ACTIVE,
    )

    alice = User.objects.create_user(
        username="neo_alice",
        email="alice@example.com",
        password="StrongPass123!"
    )

    url = reverse("node-share", args=[node.id])
    payload = {
        "emails": ["alice@example.com"],
        "access_level": "editor",
    }

    response = api_client.post(url, payload, format="json")

    assert response.status_code == 201

    response = api_client.post(url, payload, format="json")
    assert response.status_code == 201
    assert UserObjectPermission.objects.filter(user=alice).count() == 1


@pytest.mark.django_db
def test_can_share_with_existing_and_non_existing_users(user, api_client, root_folder):
    existing_user = User.objects.create_user(
        username="alice2",
        email="alice@example.com",
        password="pass",
    )

    api_client.force_authenticate(user=user)

    node = root_folder.add_child(
        name="Shared",
        owner=user,
        type=Node.NodeType.file,
        status=Node.NodeStatus.ACTIVE,
    )

    url = reverse("node-share", args=[node.id])
    payload = {
        "emails": [
            "alice@example.com",          # existing
            "newuser@example.com",        # not registered
        ],
        "access_level": "viewer",
    }

    response = api_client.post(url, payload, format="json")

    assert response.status_code == 400