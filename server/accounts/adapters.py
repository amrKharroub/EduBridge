from allauth.headless.adapter import DefaultHeadlessAdapter
from allauth.account.utils import user_display
import dataclasses
from typing import Optional

class MyHeadlessAdapter(DefaultHeadlessAdapter):
    '''This method tells Django-allauth (and OpenAPI) what fields exist and what their types are'''
    def get_user_dataclass(self):
        UserDc = super().get_user_dataclass()
        
        first_name_field = (
            "first_name", 
            Optional[str], 
            dataclasses.field(metadata={"description": "User first name", "example": "johnathen"})
        )
        last_name_field = (
            "last_name", 
            Optional[str], 
            dataclasses.field(metadata={"description": "User last name", "example": "Rees"})
        )
        fields = list(dataclasses.fields(UserDc))
        # Remove "display" if you don't want it
        # fields = [f for f in fields if f.name != "display"]
        
        # Add your new field
        # Note: make_dataclass expects a specific format: (name, type, default/field)
        custom_fields = [(f.name, f.type, f.default if f.default is not dataclasses.MISSING else dataclasses.field()) for f in fields]
        custom_fields.extend([first_name_field, last_name_field])
        
        return dataclasses.make_dataclass("User", custom_fields)
    
    def user_as_dataclass(self, user):
        '''this method actually grabs the value from the User object.'''
        UserDc = self.get_user_dataclass()
        
        # Get the standard data (you can also just manually build the dict)
        # Note: We must exclude 'display' because we removed it from the DC
        kwargs = {
            "id": str(user.pk),
            "display": user_display(user),
            "email": user.email,
            "has_usable_password": user.has_usable_password(),
            "first_name": getattr(user, "first_name", ''),
            "last_name": getattr(user, "last_name", ''),
        }
        
        if hasattr(user, "username"):
            kwargs["username"] = user.username

        return UserDc(**kwargs)