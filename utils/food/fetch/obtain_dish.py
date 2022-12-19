from django.db import transaction

from nutrition.models import *
from utils.food.parse_recipe import RecipeParser


# Obtain dish data through spoonacular.
def spoon_fetch(dish_obj: Dish):
    # Obtain the recipe.
    result = RecipeParser().get_recipe(recipe_id=dish_obj.dish_info_source.split(':')[-1])
    # Iterate through each ingredient.
    for ingredient_r in result:
        # Add the ingredient to the database.
        ingredient_obj = Ingredient(name=ingredient_r['product_name'])
        # Save the ingredient.
        ingredient_obj.save()
        # Iterate through each product.
        for product_r in ingredient_r["product_data"]["products"]:
            # Add the product.
            product_obj = Product(
                ingredient=ingredient_obj,
                ingredient_weight_in_grams=product_r['product_unit_data']['amount'],
                total_price=product_r['price']['current_unit_price']['amount'],
                auto_validity=product_r['valid'],
                extra_info=product_r
            )
            # Save the product.
            product_obj.save()
        # Save the dish ingredient.
        DishIngredient(
            dish=dish_obj,
            ingredient=ingredient_obj,
            weight_in_grams=ingredient_r["units"]["g"]
        ).save()
