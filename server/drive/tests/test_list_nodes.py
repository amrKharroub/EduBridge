import random
import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from drive.models import Node

User = get_user_model()


@pytest.fixture
def create_nodes():
    def _create(user, root_folder, number):
        statuses = [
            Node.NodeStatus.ACTIVE,
            Node.NodeStatus.UPLOADING,
            Node.NodeStatus.TRASHED,
        ]
        types = [Node.NodeType.file, Node.NodeType.folder]

        nodes = [
            root_folder.add_child(
                name="Project Docs first",
                owner=user,
                type=Node.NodeType.file,
                status=Node.NodeStatus.ACTIVE,
            )
        ]

        for i in range(number):
            nodes.append(
                root_folder.add_child(
                    name=f"Project Docs{i}",
                    owner=user,
                    type=random.choice(types),
                    status=random.choice(statuses),
                )
            )
        return nodes

    return _create


# ----------------------------------------
# Tests
# ----------------------------------------


@pytest.mark.django_db
def test_list_root_nodes(api_client, user, create_nodes):
    api_client.force_authenticate(user=user)

    root = Node.add_root(
        owner=user,
        name=f"{user.pk}Home",
        type=Node.NodeType.folder,
        status=Node.NodeStatus.ACTIVE,
    )

    nodes = create_nodes(user, root, 6)

    url = reverse("node-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == len(
        [n for n in nodes if n.status == Node.NodeStatus.ACTIVE]
    )


@pytest.mark.django_db
def test_list_nodes_inside_folder(api_client, user, root_folder, create_nodes):
    parent = root_folder.add_child(
        name="Project Docs",
        owner=user,
        type=Node.NodeType.folder,
        status=Node.NodeStatus.ACTIVE,
    )

    nodes = create_nodes(user, parent, 4)
    active_nodes = [n for n in nodes if n.status == Node.NodeStatus.ACTIVE]

    api_client.force_authenticate(user=user)

    url = reverse("node-list")
    response = api_client.get(url, {"parent_id": parent.id})

    assert response.status_code == status.HTTP_200_OK

    returned_ids = {n["id"] for n in response.data['results']}
    assert returned_ids == {n.id for n in active_nodes}


@pytest.mark.django_db
def test_list_nodes_invalid_parent_id(api_client, user):
    api_client.force_authenticate(user=user)

    url = reverse("node-list")
    response = api_client.get(url, {"parent_id": 999999})

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_list_nodes_no_access(api_client, user, root_folder):
    stranger = User.objects.create_user(
        username="stranger",
        email="stranger@test.com",
        password="StrongPass123!",
    )

    parent = root_folder.add_child(
        name="Project Docs",
        owner=user,
        type=Node.NodeType.folder,
        status=Node.NodeStatus.ACTIVE,
    )

    api_client.force_authenticate(user=stranger)

    url = reverse("node-list")
    response = api_client.get(url, {"parent_id": parent.id})

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_anonymous_user_cannot_list_nodes(api_client):
    url = reverse("node-list")
    response = api_client.get(url)

    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )


@pytest.mark.django_db
def test_file_node_cannot_be_parent(api_client, user, root_folder):
    file_node = root_folder.add_child(
        name="Project Docs",
        owner=user,
        type=Node.NodeType.file,
        status=Node.NodeStatus.ACTIVE,
    )

    api_client.force_authenticate(user=user)

    url = reverse("node-list")
    response = api_client.get(url, {"parent_id": file_node.id})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_only_direct_children_returned(api_client, user, root_folder):
    parent = root_folder.add_child(
        name="Project Docs",
        owner=user,
        type=Node.NodeType.folder,
        status=Node.NodeStatus.ACTIVE,
    )

    direct_child = parent.add_child(
        name="Project Docs2",
        owner=user,
        type=Node.NodeType.folder,
        status=Node.NodeStatus.ACTIVE,
    )

    nested_file = direct_child.add_child(
        name="Nested File",
        owner=user,
        type=Node.NodeType.file,
        status=Node.NodeStatus.ACTIVE,
    )

    api_client.force_authenticate(user=user)

    url = reverse("node-list")
    response = api_client.get(url, {"parent_id": parent.id})

    ids = {n["id"] for n in response.data['results']}

    assert nested_file.id not in ids


@pytest.mark.django_db
def test_list_nodes_response_schema(api_client, user, create_nodes):
    root = Node.add_root(
        owner=user,
        name=f"{user.pk}Home",
        type=Node.NodeType.folder,
        status=Node.NodeStatus.ACTIVE,
    )

    create_nodes(user, root, 2)

    api_client.force_authenticate(user=user)

    url = reverse("node-list")
    response = api_client.get(url)

    node = response.data['results'][0]

    assert set(node.keys()) == {"id", "name", "type", "owner"}
    assert node["type"] in {"file", "folder"}
