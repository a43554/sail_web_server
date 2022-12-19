from django.db import models
from .IngredientModel import Ingredient
from .DishModel import Dish


# The model representing a dish ingredient.
class DishIngredient(models.Model):
    # The dish this ingredient will be used in.
    dish = models.ForeignKey(Dish, null=False, on_delete=models.CASCADE)
    # The ingredient this dish ingredient references.
    ingredient = models.ForeignKey(Ingredient, null=False, on_delete=models.CASCADE)
    # The amount needed for the dish.
    weight_in_grams = models.FloatField(null=True)
