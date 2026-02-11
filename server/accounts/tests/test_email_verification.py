import pytest
from django.core import mail
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
import re
from urllib.parse import unquote


@pytest.mark.django_db
def test_email_verification_flow(api_client):
    payload = {
        "username": "johndoe",
        "first_name": "johnathen",
        "last_name": "Rees",
        "dob": "05-05-2025",
        "email": "verify@example.com",
        "password": "StrongPass123!",
    }

    response = api_client.post(
        "/_allauth/browser/v1/auth/signup",
        payload,
        format="json",
    )

    assert response.status_code == 200

    user = User.objects.get(email="verify@example.com")

    email_address = EmailAddress.objects.get(user=user)
    assert email_address.verified is False

    assert len(mail.outbox) == 1
    
    email = mail.outbox[0]
    assert "verify@example.com" in email.to

    pattern = r"https?:\/\/[\w0-9._:-]+\/account\/verify-email\/([\w%=._:-]+)\/?"
    confirmation_code = None
    for line in email.body.splitlines():
        if "http" in line:
            match_group = re.search(pattern, line)
            assert match_group is not None
            confirmation_code = unquote(match_group[1])
            break

    assert confirmation_code is not None

    verification_url = '/_allauth/browser/v1/auth/email/verify'
    custom_header = {"X-Email-Verification-Key": confirmation_code}
    confirm_response = api_client.get(verification_url, headers=custom_header)
    assert confirm_response.status_code == 200

    c_response = api_client.post(verification_url, {"key": confirmation_code}, format="json")
    assert confirm_response.status_code == 200
    email_address.refresh_from_db()
    assert email_address.verified is True

