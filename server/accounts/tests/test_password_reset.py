import pytest
from django.core import mail
from django.contrib.auth.models import User
import re

@pytest.mark.django_db
def test_password_reset_flow(api_client):
    user = User.objects.create_user(
        username="johndoe",
        email="reset@example.com",
        password="OldPassword123!"
    )

    init_response = api_client.post(
        "/_allauth/browser/v1/auth/password/request",
        {"email": "reset@example.com"},
        format="json",
    )

    assert init_response.status_code == 401

    assert len(mail.outbox) == 1
    email = mail.outbox[0]

    pattern = r"(?<=Please enter it in your open browser window.)\s+(\w+)"

    reset_code = None
    matches = re.search(pattern, email.body)

    assert matches is not None
    reset_code = matches.group(1)

    assert reset_code is not None

    reset_url = "/_allauth/browser/v1/auth/password/reset"
    reset_header = {"X-Password-Reset-Key": reset_code}
    confirm_response = api_client.get(
        reset_url,
        headers=reset_header,
    )
    
    assert confirm_response.status_code == 200 

    reset_response = api_client.post(
        reset_url,
        {
            "key": reset_code,
            "password": "NewPassword123!",
        },
        format="json",
    )

    assert reset_response.status_code == 401

    user.refresh_from_db()
    assert user.check_password("NewPassword123!")

