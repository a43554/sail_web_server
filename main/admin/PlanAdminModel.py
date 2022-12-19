from django.contrib import admin
from main.models.PlanModel import Plan
from django import forms
from django.db import models
from django_json_widget.widgets import JSONEditorWidget


# Validate.
@admin.action(description='Full deletion')
def run_full_deletion(model_admin, request, plans):
    # Iterate through each dish.
    for plan in plans:  # type: Plan
        # Validate.
        plan.full_deletion()


# The admin for the plan.
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    # The items to display in the list.
    list_display = ['name', ]

    # The actions.
    actions = [run_full_deletion, ]

    # Override the field for sources.
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
