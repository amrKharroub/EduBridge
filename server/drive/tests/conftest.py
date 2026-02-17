import pytest
from drive.models import Node
from django.contrib.auth.models import User
from rest_framework.test import APIClient
import random

@pytest.fixture
def api_client():
    return APIClient()

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