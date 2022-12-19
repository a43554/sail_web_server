from django.contrib import admin
from routing.models.RouteModel import Route
from django import forms


# The admin for the route.
@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    # The items to display in the list.
    list_display = ['expected_start_date', 'expected_end_date', ]

