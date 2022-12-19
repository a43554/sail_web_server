from django.db import models


# The model representing a meal type.
class MealType(models.Model):
    # The name of the dish.
    name = models.CharField(max_length=300, unique=True, null=False, blank=False)

    # The meal type as a string.
    def __str__(self):
        # Return the name.
        return self.name
