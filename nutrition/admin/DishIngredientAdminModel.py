from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from nutrition.models.DishIngredientModel import DishIngredient


# The admin for the dish ingredient.
@admin.register(DishIngredient)
class DishIngredientAdmin(admin.ModelAdmin):
    # The items to display in the list.
    list_display = ['ingredient_name', 'dish_name', 'weight_in_grams', ]

    # Get the ingredient name.
    def ingredient_name(self, dish_ing: DishIngredient):
        # Return the ingredient name.
        return dish_ing.ingredient.name
    # The description of the column.
    ingredient_name.short_description = 'Ingredient'

    # Get the dish name.
    def dish_name(self, dish_ing: DishIngredient):
        # Return the dish name.
        return dish_ing.dish.name
    # The description of the column.
    dish_name.short_description = 'Dish'

