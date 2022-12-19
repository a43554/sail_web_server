from django.contrib import admin
from django.db import transaction

from nutrition.models.DishModel import Dish
from utils.food.fetch.obtain_dish import spoon_fetch

# Validate.
@admin.action(description='Full deletion')
def run_full_deletion(model_admin, request, dishes):
    # Iterate through each dish.
    for dish in dishes:  # type: Dish
        # Validate.
        dish.full_delete()


# The admin for the dish.
@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    # The items to display in the list.
    list_display = ['name', 'dish_info_source']
    # The actions that can be performed.
    actions = [run_full_deletion]
    # Horizontal filters.
    filter_horizontal = ('recipe_ingredient', 'meal_type',)

    # Override the saving of the model.
    def save_model(self, request, dish: Dish, form, change):
        # Check if the dish is being created.
        is_creation = dish.pk is None
        # Create a transaction.
        with transaction.atomic():
            # Save the model.
            super().save_model(request, dish, form, change)
            # Check if model is new model.
            if is_creation:
                # Check the information source.
                if dish.dish_info_source is not None:
                    # Check if it's of type spoon.
                    if dish.dish_info_source.startswith('spoon:'):
                        # Make the request.
                        spoon_fetch(dish)
