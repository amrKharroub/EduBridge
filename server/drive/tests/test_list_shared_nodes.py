import pytest
from django.urls import reverse
from rest_framework import status
from guardian.shortcuts import assign_perm
from drive.models import Node
from django.contrib.auth.models import User
from guardian.shortcuts import get_objects_for_user

@pytest.fixture
def create_shared_node():
    def _create(owner, parent, name="Shared File", node_type=None):
        if node_type is None:
            node_type = Node.NodeType.file

        return parent.add_child(
            name=name,
            owner=owner,
            type=node_type,
            status=Node.NodeStatus.ACTIVE,
        )

    return _create


# ----------------------------------------
# Tests
# ----------------------------------------


@pytest.mark.django_db
def test_list_shared_nodes(api_client, user, root_folder, create_shared_node):
    """
    User should see nodes shared with them via guardian.
    """
    friend = User.objects.create_user(
        username="friend",
        email="friend@test.com",
        password="StrongPass123!",
    )

    shared_root = root_folder.add_child(
        owner=user,
        name=f"shared_folder",
        type=Node.NodeType.folder,
        status=Node.NodeStatus.ACTIVE,
    )

    shared_node = create_shared_node(user, shared_root)

    # Grant object-level permission
    assign_perm("drive.view_node", friend, shared_node)

    api_client.force_authenticate(user=friend)

    url = reverse("node-shared")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    returned_ids = {n["id"] for n in response.data}
    assert shared_node.id in returned_ids


@pytest.mark.django_db
def test_only_shared_nodes_returned(api_client, user, root_folder, create_shared_node):
    """
    User should only see nodes explicitly shared with them.
    """
    friend = User.objects.create_user(
        username="friend",
        email="friend@test.com",
        password="StrongPass123!",
    )

    shared_node = create_shared_node(user, root_folder, "Shared File")
    private_node = create_shared_node(user, root_folder, "Private File")

    assign_perm("view_node", friend, shared_node)

    api_client.force_authenticate(user=friend)

    url = reverse("node-shared")
    response = api_client.get(url)

    returned_ids = {n["id"] for n in response.data}

    assert shared_node.id in returned_ids
    assert private_node.id not in returned_ids


@pytest.mark.django_db
def test_shared_nodes_excludes_inactive(api_client, user, root_folder):
    """
    Shared endpoint should exclude trashed or non-active nodes.
    """
    friend = User.objects.create_user(
        username="friend",
        email="friend@test.com",
        password="StrongPass123!",
    )

    inactive_node = root_folder.add_child(
        name="Inactive",
        owner=user,
        type=Node.NodeType.file,
        status=Node.NodeStatus.TRASHED,
    )

    assign_perm("view_node", friend, inactive_node)

    api_client.force_authenticate(user=friend)

    url = reverse("node-shared")
    response = api_client.get(url)

    returned_ids = {n["id"] for n in response.data}

    assert inactive_node.id not in returned_ids


@pytest.mark.django_db
def test_no_shared_nodes_returns_empty_list(api_client, user):
    """
    If nothing is shared with the user, response should be empty list.
    """
    api_client.force_authenticate(user=user)

    url = reverse("node-shared")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_anonymous_user_cannot_access_shared_endpoint(api_client):
    """
    Anonymous users cannot access shared endpoint.
    """
    url = reverse("node-shared")
    response = api_client.get(url)

    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )

@pytest.mark.django_db
def test_owner_files_not_returned(api_client, user, root_folder, create_shared_node):
    friend = User.objects.create_user(
        username="friend",
        email="friend@test.com",
        password="StrongPass123!",
    )

    myfile = Node.add_root(
        owner=friend,
        name="Myfile",
        type=Node.NodeType.file,
        status=Node.NodeStatus.ACTIVE,
    )

    shared_node = create_shared_node(user, root_folder, "Shared File")

    assign_perm("view_node", friend, shared_node)

    api_client.force_authenticate(user=friend)

    url = reverse("node-shared")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0

    returned_ids = {n["id"] for n in response.data}

    assert myfile.id not in returned_ids

@pytest.mark.django_db
def test_shared_nodes_response_schema(api_client, user):
    """
    Response schema should match expected format.
    """
    owner = User.objects.create_user(
        username="owner4",
        email="owner4@test.com",
        password="StrongPass123!",
    )

    owner_root = Node.add_root(
        owner=owner,
        name=f"{owner.pk}Home",
        type=Node.NodeType.folder,
        status=Node.NodeStatus.ACTIVE,
    )

    node = owner_root.add_child(
        name="Shared Schema File",
        owner=owner,
        type=Node.NodeType.file,
        status=Node.NodeStatus.ACTIVE,
    )

    assign_perm("view_node", user, node)

    api_client.force_authenticate(user=user)

    url = reverse("node-shared")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    returned_node = response.data[0]

    assert set(returned_node.keys()) == {"id", "name", "type", "owner"}
    assert returned_node["type"] in {"file", "folder"}
