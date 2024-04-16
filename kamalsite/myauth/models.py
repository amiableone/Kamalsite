from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin

class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(
        max_length=255,
        unique=True,
    )
    middle_name = models.CharField(max_length=20, blank=True)
    organization = models.CharField(max_length=255, blank=True)

    def get_full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
