from django.contrib import admin
from nutrition.models.IngredientModel import Ingredient


# The admin for the ingredient.
@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    # The items to display in the list.
    list_display = ['name', ]
