from django.db import models

from .LocationModel import Location
from .RouteModel import Route


# The model representing a stop location.
class StopLocation(models.Model):
    # The route.
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    # The location.
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    # The order.
    order = models.PositiveIntegerField(null=False, blank=False)

    # Ensure there are no 2 equal stop locations.
    class Meta:
        # Make keys unique together.
        unique_together = (('route', 'location', 'order'), )
