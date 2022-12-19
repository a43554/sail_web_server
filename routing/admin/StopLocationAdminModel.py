from django.contrib import admin
from routing.models.StopLocationModel import StopLocation
from django import forms


# The admin for the stop location.
@admin.register(StopLocation)
class StopLocationAdmin(admin.ModelAdmin):
    # The items to display in the list.
    list_display = ['order', ]

