from django.db import models
from system.models.ClientModel import Client
from .PlanModel import Plan


# The model representing a plan.
class PlanAccess(models.Model):
    USER = 'USER'
    ADMIN = 'ADMIN'
    OWNER = 'OWNER'
    LEVELS = [
        (USER, 'User'),
        (ADMIN, 'Admin'),
        (OWNER, 'Owner'),
    ]
    # The plan foreign key.
    plan = models.ForeignKey(Plan, related_name='access', on_delete=models.CASCADE)
    # The user foreign key.
    user = models.ForeignKey(Client, related_name='access', on_delete=models.CASCADE)
    # If the user can make changes.
    level = models.CharField(max_length=10, default=USER, choices=LEVELS, null=False)
