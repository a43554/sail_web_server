import math
from typing import Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from django.http import HttpResponseNotFound
from scheduling.models.ScheduleModel import Schedule
from main.models.PlanModel import Plan
from nutrition.models.DishModel import Dish

# The page for displaying a schedule.
from utils.string_utils import shorten_string


class MealsSelectionPage(LoginRequiredMixin, APIView):
    # The class used for rendering.
    renderer_classes = [TemplateHTMLRenderer]
    # The template's name.
    template_name = 'demos/main/plan/meals/meals_page.html'
    # The login url.
    login_url = '/login'

    # Obtain the shift date string.
    @staticmethod
    def obtain_shift_date_string(shift: int, shifts_per_day: int) -> str:
        # Obtain the day.
        day = math.floor(shift / shifts_per_day)
        # Obtain the shift of day.
        shift_number_of_day = (shift % shifts_per_day)
        # Obtain the start time.
        start_string_time = (
                str(int(24 * (shift_number_of_day / shifts_per_day))).zfill(2)
                + ':' +
                str(int(24 * (shift_number_of_day / shifts_per_day) * 60 % 60)).zfill(2)
        )
        # Obtain the end time.
        end_string_time = (
                str(int(24 * ((shift_number_of_day + 1) / shifts_per_day))).zfill(2)
                + ':' +
                str(int(24 * ((shift_number_of_day + 1) / shifts_per_day) * 60 % 60)).zfill(2)
        )
        # Obtain the day.
        day_string = str(day).zfill(2)
        # Return the string.
        return f"{start_string_time}\n{end_string_time}"

    # The GET method for this class.
    def get(self, request, plan_id: str):
        # Attempt to get the plan.
        plan = Plan.objects.filter(id=plan_id).first()
        # Check if not schedule was found.
        if plan is None:
            # Raise the 404 exception.
            return HttpResponseNotFound(f'No plan with ID \'{plan_id}\' was found.')
        # The selected meals.
        selected_meals = plan.plan_meal.possible_meals.all()
        # Obtain all dishes and parse them to json.
        all_dishes = [{
            # The meal's name.
            'name': meal.name,
            # The description.
            'description': meal.description,
            # Check if already selected.
            'selected': meal in selected_meals,
            # The meal's type.
            'meal_type': str(meal.meal_type),
            # The ingredient data.
            'dish_ingredients': [{
                # The ingredient's name.
                'name': dish_ingredient.ingredient.name,
                # The amount (in grams).
                'amount': dish_ingredient.weight_in_grams
            } for dish_ingredient in meal.dishingredient_set.all()]
        } for meal in Dish.objects.all()]
        # Map the context.
        context = {
            # Store the solutions.
            'schedule_data': {
                # Store the tasks.
                'tasks': [],
                # The name of the various people.
                'crew': [],
                # The various shifts.
                'shifts': [],
                # The shift info by crew member.
                'shifts_by_crew': []
            },
            # Meal information.
            'nutrition_data': {
                # All possible menus.
                'all_menus': [{
                    # The meal's name.
                    'name': meal['name'],
                    # The description.
                    'description': {
                        # The short description.
                        'short': shorten_string(meal['description'], 240),
                        # The full description.
                        'full': meal['description'],
                    },
                    # Check if already selected.
                    'selected': meal['selected'],
                    # The meal's type.
                    'meal_type': meal['meal_type'],
                    # The ingredient data.
                    'ingredient_data': {
                        # The ingredient short list.
                        'short': shorten_string(', '.join([ing['name'] for ing in meal['dish_ingredients']]), 120),
                        # The list of ingredients.
                        'ingredient_list': [{
                            # The ingredient's name.
                            'name': dish_ingredient['name'],
                            # The amount (in grams).
                            'amount': dish_ingredient['amount']
                        } for dish_ingredient in meal['dish_ingredients']]
                    }
                } for meal in all_dishes],
            }
        }
        # Return the response with the html content.
        return Response(context)
