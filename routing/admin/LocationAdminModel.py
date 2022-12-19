from django.contrib import admin
from routing.models.LocationModel import Location
from django import forms


# The admin for the location.
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    # The items to display in the list.
    list_display = ['latitude', 'longitude', ]

