from django.db import models

from .ScheduleModel import Schedule
from utils.new.ScheduleOptions import ScheduleOptions
from system.models.ClientModel import Client


# The model representing a task.
class Task(models.Model):
    # The task identifying name.
    name = models.CharField(max_length=150, null=False)
    # The task display name.
    display_name = models.CharField(max_length=150, null=True)
    # The task description.
    task_description = models.TextField(max_length=500, null=True, blank=True)
    # The task category.
    task_category = models.CharField(max_length=50, null=True)
    # The task sub-category.
    task_sub_category = models.CharField(max_length=50, null=True)
    # Tasks incompatible with the current one.
    incompatible_person_tasks = models.ManyToManyField('self', blank=True)
    # The handlers that are qualified to handle this task.
    qualified_members = models.ManyToManyField(Client, blank=True, related_name='task_qualifications')
    # Extra settings.
    advanced_settings = models.JSONField(null=False, default=ScheduleOptions.get_default_settings)
    # The tasks this schedule has.
    schedule = models.ForeignKey(Schedule, related_name='tasks', on_delete=models.CASCADE)

    # The to string method of this object.
    def __str__(self):
        # Return the name.
        return f'{self.name} [{self.task_category}/{self.task_sub_category}]'
