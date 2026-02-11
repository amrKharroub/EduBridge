from django import forms
from accounts.models import UserProfile
from django.db import transaction

class CustomSignupForm(forms.Form):
    first_name = forms.CharField(
        max_length=30,
        required=False
    )
    last_name = forms.CharField(
        max_length=30,
        required=False
    )
    dob = forms.DateField(
        input_formats=['%d/%m/%Y', '%d-%m-%Y'],
        required=False
    )

    def signup(self, request, user):
        "this function runs after the user is created but before it is saved to the db"
        with transaction.atomic():
            UserProfile.objects.create(
                user=user,
                dob=self.cleaned_data.get('dob')
            )