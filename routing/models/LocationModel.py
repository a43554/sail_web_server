from django.db import models


# The model representing a location.
class Location(models.Model):
    # The latitude of the location.
    latitude = models.FloatField()
    # The longitude of the location.
    longitude = models.FloatField()
