from django.db import models
from django.contrib.auth.models import AbstractUser

# TODO:
#   To make site useful in tracking inventory and production
#   status based on both retail and wholesale sales, it is
#   likely that admins will have to create wholesale orders
#   on behalf of some wholesale clients that will not bother
#   themselves with these CAN'T REMEMBER THE TERM.

class User(AbstractUser):
    pass
