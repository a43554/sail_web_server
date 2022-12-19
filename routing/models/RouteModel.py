from django.db import models

from .LocationModel import Location


# The model representing a task.
class Route(models.Model):
    # The start location.
    start_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='route_starts')
    # The end location.
    end_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='route_ends')
    # All the stops until the end location.
    stop_locations = models.ManyToManyField(Location, through='StopLocation', blank=True, related_name='route_stops')
    # The start date of the route.
    expected_start_date = models.DateTimeField(null=True,)
    # The end date of the route.
    expected_end_date = models.DateTimeField(null=True)
