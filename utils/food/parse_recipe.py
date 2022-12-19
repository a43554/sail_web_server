import json

import requests
from bs4 import BeautifulSoup

from utils.food.fetch.handle_product import ProductHandler
from utils.none import default_if_none, run_if_none


class RecipeParser:
    # The authentication key.
    AUTH = '87e0ff75f9d44c299372d20b8b179dd8'

    # Parse the price data.
    def parse_prices(self, product) -> dict:
        # Obtain the primary price.
        primary_price_node = product.find('span', {'class': 'sales ct-tile--price-primary'})
        # Obtain the true price.
        primary_price = float(
            primary_price_node
            .find('span', {'class': 'ct-price-formatted'})
            .text.strip().replace('€', '').replace(',', '.')
        )
        # Obtain the units.
        primary_price_units = (
            primary_price_node
            .find('span', {'class': 'ct-m-unit'})
            .text.strip().replace('/', '')
        )
        # Obtain the discount, if it exists.
        discount = default_if_none(
            data=product.find('p', {'class': 'ct-discount-amount'}),
            if_none=0.0,
            if_not_none=(
                lambda p: (int(p.text.split(':')[-1].strip().replace('%', '')) / 100.0) if "Desconto" in p.text else 0.0
            )
        )
        # Check if discount exists.
        if discount > 0:
            # Obtain the previous price.
            previous_price_node = product.find('span', {'class': 'strike-through list ct-tile--price-dashed'})
            # Obtain the true price.
            previous_price = float(
                previous_price_node
                .find('span', {'class': 'sr-only'}).next_sibling
                .text.strip().replace('€', '').replace(',', '.')
            )
            # Obtain the units.
            previous_price_units = (
                previous_price_node
                .find('span', {'class': 'ct-tile--price-dashed'})
                .text.strip().replace('/', '')
            )
            # The previous uni price.
            previous_unit_price = {
                'amount': previous_price,
                'units': previous_price_units
            }
        # Otherwise, use none.
        else:
            # No previous price.
            previous_unit_price = None

        # Obtain the secondary price.
        secondary_price_node = product.find('div', {'class': 'ct-tile--price-secondary'})
        # Obtain the true price.
        secondary_price = float(
            secondary_price_node
            .find('span', {'class': 'ct-price-value'})
            .text.strip().replace('€', '').replace(',', '.')
        )
        # Obtain the units.
        secondary_price_units = (
            secondary_price_node
            .find('span', {'class': 'ct-m-unit'})
            .text.strip().replace('/', '')
        )
        # Return the price data.
        return {
            'current_unit_price': {
                'amount': primary_price,
                'units': primary_price_units
            },
            'current_price': {
                'amount': secondary_price,
                'units': secondary_price_units
            },
            'discount': discount,
            'previous_unit_price': previous_unit_price
        }

    # Convert the amount to grams.
    def weight_as_grams(self, ingredient_name: str, original_unit: str, amount: float) -> float:
        # Make the request.
        response = requests.get(url='https://api.spoonacular.com/recipes/convert', params={
            'apiKey': RecipeParser.AUTH,
            'ingredientName': ingredient_name,
            'sourceAmount': amount,
            'sourceUnit': original_unit,
            'targetUnit': 'g',
        })
        # Parse the response.
        json_response = response.json()
        # Return the amount in grams.
        return json_response['targetAmount']

    # Obtain the recipe.
    def get_recipe(self, recipe_id: str) -> list:
        # Import translations.
        import translators as ts
        # Make the request.
        response = requests.get(url=f'https://api.spoonacular.com/recipes/{recipe_id}/information', params={
            'apiKey': RecipeParser.AUTH,
            'includeNutrition': False
        })
        # Obtain the json response.
        json_response = response.json()
        # The ingredient data.
        ingredient_data_list = []
        # Iterate through each ingredient.
        for server_ingredient in json_response['extendedIngredients']:
            print(f"Ingredient: {server_ingredient['name']}")  # LOG
            # Ingredient info.
            ingredient_data = {
                'product_name': server_ingredient['name'],
                'original_data': server_ingredient,
                'units': {}
            }
            # Insert the measure.
            ingredient_data['units'][server_ingredient['unit']] = server_ingredient['amount']
            # Iterate through each measurement.
            for measure_info in server_ingredient['measures'].values():
                # Insert the measure.
                ingredient_data['units'][measure_info['unitShort']] = measure_info['amount']
            # Check to see if units 'g' or 'kg' are present in the dictionary.
            if 'kg' in ingredient_data['units']:
                # Convert the amount to grams.
                ingredient_data['units']['g'] = ingredient_data['measures']['kg'] * 1000
            # Check if the ingredient unit is not in grams.
            elif 'g' not in ingredient_data['units']:
                # Convert the amount to grams.
                ingredient_data['units']['g'] = self.weight_as_grams(
                    ingredient_name=server_ingredient['name'],
                    original_unit=server_ingredient['unit'],
                    amount=server_ingredient['amount']
                )
            print(f"\t- Amount: {' // '.join([f'{v_amount} ({k_unit})' for k_unit, v_amount in ingredient_data['units'].items()])}")  # LOG
            # Translate the ingredient.
            ingredient_data['product_name_pt'] = ts.google(
                ingredient_data['product_name'], to_language='pt'
            ).replace(' -', '-').replace('- ', '-')
            print(f"\t- Translated Name: {ingredient_data['product_name_pt']}")  # LOG
            # Obtain the product list.
            has_valid_product, search_fail, product_list = ProductHandler.parse_products(ingredient_data)
            # Set the product info into the data.
            ingredient_data['product_data'] = {
                'validity': {
                    'match_found': search_fail,
                    'found_results': len(product_list) > 0,
                    'valid_amount': has_valid_product
                },
                'products': product_list
            }
            # Mark as complete or not.
            ingredient_data['complete'] = (
                ingredient_data['product_data']['validity']['match_found'] and
                ingredient_data['product_data']['validity']['found_results'] and
                ingredient_data['product_data']['validity']['valid_amount']
            )
            # Append the data to the list.
            ingredient_data_list.append(ingredient_data)
        # Return the json data.
        return ingredient_data_list


if __name__ == "__main__":

    id_list = [
        ('TEST_1', '782600'),
        # ('TEST_2', '654959'),
        # ('TEST_3', '716426'),
        # ('TEST_4', '1095986'),
        # ('TEST_5', '642230')
    ]

    for recipe_id_name, recipe_id in id_list:

        result = RecipeParser().get_recipe(recipe_id=recipe_id)

        with open('../utils/food/test.json', 'w+') as f:
            json.dump(result, f)

        # # # # # # # # # # TEST WITH DJANGO # # # # # # # # # #
        import utils.quickstart
        from django.db import transaction
        from nutrition.models import *

        # Create a transaction.
        with transaction.atomic():
            # The dish's name.
            dish_name = recipe_id_name
            # Try to obtain the dish if it exists.
            run_if_none(Dish.objects.filter(name=dish_name).first(), if_not_none=(lambda d: d.full_delete()))
            # Create the dish.
            dish_obj = Dish(name=dish_name)
            # Save the dish.
            dish_obj.save()
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
        print("")