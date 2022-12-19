from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from nutrition.models.MenuModel import Menu


# Validate.
@admin.action(description='Make Schedule')
def run_make_schedule(model_admin, request, menus):
    # Iterate through each dish.
    for menu in menus:  # type: Menu
        # Validate.
        menu.generate_schedule()


# The admin for the dish.
@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    # The items to display in the list.
    list_display = ['name', ]
    # Horizontal filters.
    filter_horizontal = ('possible_meals',)
    # The actions that can be performed.
    actions = [run_make_schedule]
    # Override the field for sources.
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
