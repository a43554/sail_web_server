from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from system.managers.ClientManager import ClientManager


# The client model object.
class Client(AbstractUser, PermissionsMixin):
    # Remove unused fields.
    first_name, last_name, email = None, None, None
    # The display name field.
    full_name = models.CharField(max_length=200, blank=True)

    # The required fields.
    REQUIRED_FIELDS = []

    # The manager.
    objects = ClientManager()

    # The string representation of the object.
    def __str__(self):
        # Return the username.
        return self.username
