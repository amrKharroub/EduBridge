import pytest
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_authenticated_user_can_logout(api_client):
    User.objects.create_user(
        username="johndoe",
        email="logout@example.com",
        password="StrongPass123!"
    )

    api_client.login(username="johndoe", password="StrongPass123!")

    response = api_client.delete(
        "/_allauth/browser/v1/auth/session"
    )

    assert response.status_code == 401

    data = response.json()

    assert data["meta"]["is_authenticated"] is False

    flow_ids = {flow["id"] for flow in data["data"]["flows"]}

    assert "login" in flow_ids
    assert "signup" in flow_ids


@pytest.mark.django_db
def test_logout_when_not_authenticated(api_client):
    response = api_client.delete(
        "/_allauth/browser/v1/auth/session"
    )

    assert response.status_code == 401

    data = response.json()

    assert data["meta"]["is_authenticated"] is False

    flow_ids = {flow["id"] for flow in data["data"]["flows"]}

    assert "login" in flow_ids
    assert "signup" in flow_ids