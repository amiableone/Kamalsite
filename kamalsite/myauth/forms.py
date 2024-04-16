from django.contrib.auth.forms import UserCreationForm
from .models import User


class MyUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        # include custom fields:
        fields = UserCreationForm.Meta.fields + (
            "middle_name",
            "organization",
        )
