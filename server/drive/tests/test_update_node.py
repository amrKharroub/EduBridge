import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_owner_can_make_node_public(api_client, user, node):
    api_client.force_authenticate(user=user)

    url = reverse("update-node", kwargs={"pk": node.id})
    payload = {"is_public": True}

    response = api_client.patch(url, payload, format="json")

    assert response.status_code == status.HTTP_200_OK

    node.refresh_from_db()
    assert node.is_public is True


def test_owner_can_rename_node(api_client, user, node):
    api_client.force_authenticate(user=user)

    url = reverse("update-node", kwargs={"pk": node.id})
    payload = {"name": "new Name"}

    response = api_client.patch(url, payload, format="json")

    assert response.status_code == status.HTTP_200_OK

    node.refresh_from_db()
    assert node.name == "new Name"


def test_non_owner_cannot_change_visibility(api_client, node):
    other_user = User.objects.create_user(
        username="other",
        email="other@test.com",
        password="StrongPass123!"
    )
    api_client.force_authenticate(user=other_user)

    url = reverse("update-node", kwargs={"pk": node.id})
    payload = {"is_public": True}

    response = api_client.patch(url, payload, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN

    node.refresh_from_db()
    assert node.is_public is False


def test_anonymous_user_cannot_change_visibility(api_client, node):
    url = reverse("update-node", kwargs={"pk": node.id})
    payload = {"is_public": True}

    response = api_client.patch(url, payload, format="json")

    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )

    node.refresh_from_db()
    assert node.is_public is False


def test_empty_payload_changes_nothing(api_client, user, node):
    api_client.force_authenticate(user=user)

    url = reverse("update-node", kwargs={"pk": node.id})

    response = api_client.patch(url, {}, format="json")

    assert response.status_code == status.HTTP_200_OK
    node.refresh_from_db()
    assert node.is_public is False


def test_change_visibility_node_not_found(api_client, user):
    api_client.force_authenticate(user=user)

    url = reverse("update-node", kwargs={"pk": 999999})
    payload = {"is_public": True}

    response = api_client.patch(url, payload, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_make_public_when_already_public(api_client, user, node):
    node.is_public = True
    node.save()

    api_client.force_authenticate(user=user)

    url = reverse("update-node", kwargs={"pk": node.id})
    payload = {"is_public": True}

    response = api_client.patch(url, payload, format="json")

    assert response.status_code == status.HTTP_200_OK

    node.refresh_from_db()
    assert node.is_public is True


def test_make_private_when_public(api_client, user, node):
    node.is_public = True
    node.save()

    api_client.force_authenticate(user=user)

    url = reverse("update-node", kwargs={"pk": node.id})
    payload = {"is_public": False}

    response = api_client.patch(url, payload, format="json")

    assert response.status_code == status.HTTP_200_OK

    node.refresh_from_db()
    assert node.is_public is False