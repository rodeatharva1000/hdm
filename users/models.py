from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    can_reply = models.BooleanField(default=False)