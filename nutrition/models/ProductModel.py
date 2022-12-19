from django.db import models
from .IngredientModel import Ingredient


# The model representing a product.
class Product(models.Model):
    # The ingredient this product references.
    ingredient = models.ForeignKey(Ingredient, null=False, on_delete=models.CASCADE)
    # The product amount in grams.
    ingredient_weight_in_grams = models.FloatField(null=True)
    # Additional product weight.
    non_ingredient_weight_in_grams = models.FloatField(null=False, default=0.0)
    # The product's price.
    total_price = models.FloatField(null=True)
    # The validity of this product information.
    auto_validity = models.BooleanField(null=True, default=None)
    # If the product has been manually validated.
    manual_validation = models.BooleanField(null=False, default=False)
    # Other information.
    extra_info = models.JSONField(null=True, blank=True)

