from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from nutrition.models.MealType import MealType

# The admin for the meal type.
@admin.register(MealType)
class MealTypeAdmin(admin.ModelAdmin):
    # The items to display in the list.
    list_display = ['name', ]
