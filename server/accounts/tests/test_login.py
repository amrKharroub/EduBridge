import pytest
from django.contrib.auth.models import User 

@pytest.mark.django_db
def test_user_can_login_with_username(api_client):
    User.objects.create_user(
        username="johndoe",
        email="test@example.com",
        password="StrongPass123!"
    )

    payload = {
        "username": "johndoe",
        "password": "StrongPass123!",
    }

    response = api_client.post(
        "/_allauth/browser/v1/auth/login",
        payload,
        format="json",
    )

    assert response.status_code == 200

@pytest.mark.django_db
def test_user_can_login_with_email(api_client):
    User.objects.create_user(
        username="johndoe",
        email="test@example.com",
        password="StrongPass123!"
    )

    payload = {
        "email": "test@example.com",
        "password": "StrongPass123!",
    }

    response = api_client.post(
        "/_allauth/browser/v1/auth/login",
        payload,
        format="json",
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_login_with_wrong_password_fails(api_client):
    User.objects.create_user(
        username="johndoe",
        email="test@example.com",
        password="StrongPass123!"
    )

    payload = {
        "email": "test@example.com",
        "password": "WrongPass!",
    }

    response = api_client.post(
        "/_allauth/browser/v1/auth/login",
        payload,
        format="json",
    )

    assert response.status_code == 400