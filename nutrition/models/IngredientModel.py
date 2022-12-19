from django.db import models


# The model representing an ingredient.
class Ingredient(models.Model):
    # The name of the ingredient.
    name = models.CharField(max_length=300, unique=False, null=False, blank=False)

    # The to string of this ingredient.
    def __str__(self):
        # Return the ingredient name.
        return self.name
