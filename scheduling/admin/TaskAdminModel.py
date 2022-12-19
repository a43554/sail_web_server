from django.contrib import admin
from django.db import models
from scheduling.models.TaskModel import Task
from django_json_widget.widgets import JSONEditorWidget

# The admin for the task.
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    # The items to display in the list.
    list_display = ['name', 'task_category', 'task_sub_category', ]
    # Search filters.
    search_fields = ('task_category',)
    # Horizontal filters.
    filter_horizontal = ('incompatible_person_tasks', 'qualified_members')
    # Override the field for sources.
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

