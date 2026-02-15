import pytest
from drive.models import Node
from django.contrib.auth.models import User
from rest_framework.test import APIClient

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