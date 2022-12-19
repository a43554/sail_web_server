from django.db import models, transaction

from utils.food.MealSchedule import MealSchedule
from . import DishIngredient, Product
from ..models.DishModel import Dish
from django.utils.translation import gettext_lazy as _
from .IngredientModel import Ingredient
from .MealType import MealType


# The model representing a dish.
class Menu(models.Model):
    NONE = 'NONE'
    PRICE = 'PRICE'
    WEIGHT = 'WEIGHT'

    # The name of the dish.
    name = models.CharField(max_length=300, unique=False, null=False, blank=False, default='-')
    # The possible meals that can be found in the plan.
    possible_meals = models.ManyToManyField(Dish, blank=True)
    # Meal list.
    meal_times = models.JSONField(null=True, default=list, blank=True)
    # The product priority.
    product_priority = models.CharField(null=False, default=NONE, max_length=100)
    # The possible solutions.
    last_solutions = models.JSONField(null=True, default=dict, blank=True)

    # The meta information.
    class Meta:
        # The plural name of the object.
        verbose_name_plural = "Menus"

    # The multiplier to not use floats.
    K_SCALE = 1000

    # The dish as a string.
    def __str__(self):
        # Return the name.
        return self.name

    # Produce the data necessary to be parsed.
    def generate_schedule(self):
        # The list of all meals.
        meals = {}
        # The used products.
        products = {}
        # Iterate through all possible meals.
        for dish in self.possible_meals.all():
            # Construct the dish info.
            dish_info = ({
                'meal_types': [meal_type.name for meal_type in dish.meal_type.all()],
                'ingredients': {}
            })
            # Iterate through all ingredients.
            for ingredient in dish.recipe_ingredient.all():
                # Obtain the dish ingredient connection.
                dish_ingredient = DishIngredient.objects.filter(ingredient=ingredient, dish=dish).first()
                # Obtain the most recent product for this ingredient.
                matching_product = ingredient.product_set.first()  # type: Product
                # Add the product information.
                products.setdefault(ingredient.id, {
                    'product': matching_product.id,
                    'weight': int(matching_product.ingredient_weight_in_grams * self.K_SCALE),
                    'price': matching_product.total_price,
                    'menus': []
                })['menus'].append(dish.id)
                # Append to the dish information.
                dish_info['ingredients'][ingredient.id] = {
                    'weight': int(dish_ingredient.weight_in_grams * self.K_SCALE)
                }
            # Append it to the meal list.
            meals[dish.id] = dish_info
        # Run the solver.
        self.last_solutions = MealSchedule(
            self.meal_times,
            self.plan.assigned_users.count(),
            meals,
            products,
            self.product_priority
        ).solve()
        # Make sure to re-scale the weight.
        for key, solution in self.last_solutions.items():
            # Re-scale the total weight.
            solution['totals']['weight'] = float(solution['totals']['weight'] / self.K_SCALE)
        # Save the data.
        self.save()
