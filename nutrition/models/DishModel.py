from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from .IngredientModel import Ingredient
from .MealType import MealType


# The model representing a dish.
class Dish(models.Model):
    # The name of the dish.
    name = models.CharField(max_length=300, unique=False, null=False, blank=False)
    # Search identification.
    dish_info_source = models.CharField(max_length=100, null=True, blank=True)
    # The description of this dish.
    description = models.TextField(null=True, blank=True, default='')
    # The ingredients to be used.
    recipe_ingredient = models.ManyToManyField(Ingredient, through='DishIngredient')
    # The meal type of this dish.
    meal_type = models.ManyToManyField(MealType)

    # The meta information.
    class Meta:
        # The plural name of the object.
        verbose_name_plural = "dishes"

    # The dish as a string.
    def __str__(self):
        # Return the name.
        return self.name

    # Remove the dish and any unused ingredients from the database.
    def full_delete(self):
        # Create a transaction.
        with transaction.atomic():
            # Iterate though each ingredient in this dish.
            for recipe_ingredient in self.recipe_ingredient.all():
                # Check if any other dishes use this ingredient.
                if recipe_ingredient.dish_set.count() == 1:
                    # Obtain the dish-ingredient pair model.
                    dish_ingredient_obj = recipe_ingredient.dishingredient_set.get(dish=self)
                    # Only the current dish uses this ingredient, remove the dish ingredient.
                    dish_ingredient_obj.delete()
                    # Only the current dish uses this ingredient, remove the ingredient.
                    recipe_ingredient.delete()
            # Finally, delete the dish.
            self.delete()
