from django.contrib import admin
from main.models.PlanAccessModel import PlanAccess
from django import forms
from django.db import models
from django_json_widget.widgets import JSONEditorWidget


# The admin for the plan.
@admin.register(PlanAccess)
class PlanAccessAdmin(admin.ModelAdmin):
    # The items to display in the list.
    list_display = ['plan', 'user', 'level', ]
