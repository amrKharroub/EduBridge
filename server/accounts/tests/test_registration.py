import pytest
from django.contrib.auth.models import User 
from accounts.models import UserProfile


@pytest.mark.django_db
def test_user_can_register(api_client):
    payload = {
        "username": "johndoe",
        "first_name": "johnathen",
        "last_name": "Rees",
        "dob": "05-05-2025",
        "email": "test@example.com",
        "password": "StrongPass123!",
    }

    response = api_client.post(
        "/_allauth/browser/v1/auth/signup",
        payload,
        format="json",
    )

    assert response.status_code == 200

    user = User.objects.get(email="test@example.com")
    profile = UserProfile.objects.get(user=user)

    assert profile.dob.strftime('%d/%m/%Y') == "05/05/2025"
    assert User.objects.filter(email="test@example.com").exists()
    assert UserProfile.objects.filter(user__email="test@example.com").exists()



@pytest.mark.django_db
def test_duplicate_email_registration_fails(api_client):
    User.objects.create_user(
        username="johndoe",
        email="test@example.com",
        password="StrongPass123!"
    )

    payload = {
        "username": "johndoe",
        "first_name": "johnathen",
        "last_name": "Rees",
        "email": "test@example.com",
        "password": "StrongPass123!",
    }

    response = api_client.post(
        "/_allauth/browser/v1/auth/signup",
        payload,
        format="json",
    )

    assert response.status_code == 400