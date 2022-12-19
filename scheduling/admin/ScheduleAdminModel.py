from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from scheduling.models.ScheduleModel import Schedule


# Create the schedule.
@admin.action(description='Prepare Schedule')
def make_schedules(model_admin, request, schedules):
    # Iterate through each schedule.
    for schedule in schedules:  # type: Schedule
        # Create the parser.
        schedule.reload_schedule()


# The admin for the task.
@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    # The actions available.
    actions = [make_schedules]
    # Override the field for sources.
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
