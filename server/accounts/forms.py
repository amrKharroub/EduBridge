from django import forms
from accounts.models import UserProfile

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
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()

        profile = UserProfile(user=user)
        profile.dob = self.cleaned_data.get('dob')
        profile.save()