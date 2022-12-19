import functools
import math
import random
from datetime import datetime
from typing import Iterable

from main.models import Plan, PlanAccess
from nutrition.models import Dish, Product
from routing.models import StopLocation


# Execute operations on the progress dictionaries.
from scheduling.models import Task
from utils.string_utils import shorten_string


class PlanOperations:

    @staticmethod
    def get_plan_route_path(plan: Plan):
        # Full data array.
        data_dict = {
            'start': {'lat': '', 'long': ''},
            'finish': {'lat': '', 'long': ''},
            'stops': []
        }
        # Obtain the route, if it exists.
        plan_route = plan.plan_route
        # Check if it exists.
        if plan_route is not None:
            # Set the start location.
            if plan_route.start_location is not None:
                # Update it.
                data_dict['start'] = {
                    'lat': plan_route.start_location.latitude,
                    'long': plan_route.start_location.longitude,
                }
            # Set the end location.
            if plan_route.end_location is not None:
                # Update it.
                data_dict['finish'] = {
                    'lat': plan_route.end_location.latitude,
                    'long': plan_route.end_location.longitude,
                }
            # Obtain all stops.
            for stop_data in StopLocation.objects.filter(route=plan_route).order_by('order').all():
                # Update the array.
                data_dict['stops'].append({
                    'lat': stop_data.location.latitude,
                    'long': stop_data.location.longitude,
                })
        # Return the dictionary.
        return data_dict

    @staticmethod
    def get_plan_route_duration(plan: Plan):
        # Full data array.
        data_dict = {
            'start': "",
            'finish': "",
        }
        # Obtain the route, if it exists.
        plan_route = plan.plan_route
        # Check if it exists.
        if plan_route is not None:
            # Set the start time.
            if plan_route.expected_start_date is not None:
                # Update it.
                data_dict['start'] = plan_route.expected_start_date.date().strftime('%d/%m/%Y')
            # Set the end time.
            if plan_route.expected_end_date is not None:
                # Update it.
                data_dict['finish'] = plan_route.expected_end_date.date().strftime('%d/%m/%Y')
        # Return the dictionary.
        return data_dict

    @staticmethod
    def get_plan_assignments_settings(plan: Plan):
        # Full data array.
        data_dict = {
            'total_shifts': "",
            'total_days': "",
            'daily_shifts': "",
        }
        # Obtain the route, if it exists.
        plan_schedule = plan.plan_schedule
        # Check if it exists.
        if plan_schedule is not None:
            # Set the total shifts.
            if plan_schedule.total_shift_amount is not None:
                # Update it.
                data_dict['total_shifts'] = plan_schedule.total_shift_amount
            # Set the daily shifts.
            if plan_schedule.total_shifts_per_day is not None:
                # Update it.
                data_dict['daily_shifts'] = plan_schedule.total_shifts_per_day
            # Check if both aren't none.
            if plan_schedule.total_shifts_per_day is not None and plan_schedule.total_shift_amount is not None:
                # Update it.
                data_dict['total_days'] = int(plan_schedule.total_shift_amount / plan_schedule.total_shifts_per_day)
        # Return the dictionary.
        return data_dict

    @staticmethod
    def two_dimensional_calendar(days, daily_shifts, valid_shift_list):
        # Create the full data array.
        full_array = []
        # Iterate through all daily shifts.
        for day_shift in range(0, daily_shifts):
            # The inner array.
            inner_array = []
            # Iterate through the days.
            for day in range(0, days):
                # Add true if present, false otherwise.
                inner_array.append(((day * daily_shifts) + day_shift) in valid_shift_list)
            # Add the inner array.
            full_array.append(inner_array)
        # Return the full array
        return full_array

    @staticmethod
    def get_plan_assignments_tasks(plan: Plan):
        # Check if schedule exists.
        if plan.plan_schedule is None:
            # Return nothing.
            return []
        # Return all plans.
        return [{
            'status': plan.plan_maker_progress[task.name],
            'content': {
                'true_id': task.name,
                'id': task.name.replace('assignments_tasks_', 'Tarefa '),
                'name': task.display_name,
                'description': task.task_description,
                'valid_shifts': PlanOperations.two_dimensional_calendar(
                    math.floor(plan.plan_schedule.total_shift_amount / plan.plan_schedule.total_shifts_per_day),
                    plan.plan_schedule.total_shifts_per_day,
                    task.advanced_settings['valid_shifts']['setting_value']
                ),
                'qualified_members': [user.id for user in task.qualified_members.all()],
                'incompatible_tasks': [other_task.name for other_task in task.incompatible_person_tasks.all()],
                'sequential_settings': task.advanced_settings['sequential_settings']['setting_value'],
                'people_per_shift_task': task.advanced_settings['people_per_shift_task']['setting_value'],
                'per_task_cycle_settings': task.advanced_settings['per_task_cycle_settings']['setting_value'],
                'per_person_cycle_settings': task.advanced_settings['per_person_cycle_settings']['setting_value'],
            }
        } for task in plan.plan_schedule.tasks.all().order_by('name')] # if task.name in plan.plan_maker_progress]

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

    @staticmethod
    def get_plan_assignments_schedule(plan: Plan):
        # Check if schedule exists.
        if plan.plan_schedule is None:
            # Return nothing.
            return []
        # Obtain the times.
        times = [
            [
                PlanOperations.obtain_shift_date_string(i, plan.plan_schedule.total_shifts_per_day)
            ] for i in range(plan.plan_schedule.total_shift_amount)
        ]
        # The crew members.
        crew = [handler.username for handler in plan.assigned_users.all()]
        # Obtain the solution values.
        shift_values = list(list(plan.plan_schedule.last_solutions.values())[0].values()) if plan.plan_schedule.last_solutions != {} else []
        # The full table list.
        full_member_table = []
        full_task_table = []
        # Iterate through each shift value.
        for idx, task_info in enumerate(shift_values):
            # The current row by member.
            columns_by_member = []
            columns_by_task = [[] for _ in task_info.items()]
            # Obtain the current time.
            current_time = times[idx]
            # Iterate through each crew member.
            for m_idx, member in enumerate(crew):
                # Tasks per member.
                tasks_by_member = []
                # Iterate through each task name.
                for t_idx, t_data in enumerate(task_info.items()):
                    # Obtain the needed data.
                    t_name, t_crew = t_data
                    # Filter by the ones containing a crew member.
                    if member in t_crew:
                        # Get the task information.
                        task_name = Task.objects.get(name=t_name, schedule__plan=plan).display_name
                        # Add the member.
                        columns_by_task[t_idx].append(member)
                        # Add the task.
                        tasks_by_member.append(task_name)
                # Store the tasks per member in the upper array.
                columns_by_member.append(tasks_by_member)
            # Append it to the full list.
            full_member_table.append([current_time] + columns_by_member)
            full_task_table.append([current_time] + columns_by_task)

        # Return the table.
        return {
            'crew': crew,
            'table': full_member_table,
            'tasks': [
                Task.objects.get(name=t_name, schedule__plan=plan).display_name for t_name in shift_values[0].keys()
            ] if len(shift_values) > 0 else [],
            'r_table': full_task_table
        }

    @staticmethod
    def get_plan_meals_settings(plan: Plan):
        # Check if schedule exists.
        if plan.plan_meal is None:
            # Return nothing.
            return []
        # Obtain the times.
        return {
            'meals': plan.plan_meal.meal_times,
            'priority': plan.plan_meal.product_priority
        }

    @staticmethod
    def get_plan_meals_selection(plan: Plan):
        # Check if schedule exists.
        if plan.plan_meal is None:
            # The selected meals.
            selected_meals = []
        else:
            # The selected meals.
            selected_meals = plan.plan_meal.possible_meals.all()
        # Obtain all dishes and parse them to json.
        all_dishes = [{
            # The meal's name.
            'name': meal.name,
            # The dish id.
            'id': meal.id,
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
        } for meal in Dish.objects.filter(recipe_ingredient__product__manual_validation=True).distinct()]
        # Map the context.
        return {
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
                    # The dish id.
                    'id': meal['id'],
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
                            'amount': f"{dish_ingredient['amount']}"
                        } for dish_ingredient in meal['dish_ingredients']]
                    }
                } for meal in all_dishes],
            }
        }

    @staticmethod
    def sum_and_reduce(curr, dictionary: dict):
        # obtain the key.
        key = curr[0]
        # Check if curr is in dictionary.
        if key in dictionary:
            # Append the value.
            dictionary[key] += curr[1]
        else:
            dictionary[key] = curr[1]
        return dictionary

    @staticmethod
    def get_plan_meals_schedule(plan: Plan):
        # Check if schedule exists.
        if plan.plan_meal is None or len(plan.plan_meal.last_solutions) == 0:
            # Return nothing.
            return {}
        # Return a random result from the dictionary.
        meal_schedule = list(plan.plan_meal.last_solutions.values())[0]
        # The user's count.
        user_count = plan.assigned_users.count()
        # Total dictionary.
        totals_dict = {
            'ingredients': {},
            'dishes': {}
        }
        # Iterate through each menu id.
        for m_id in meal_schedule['schedule'].values():
            # Obtain the dish.
            dish = Dish.objects.filter(id=m_id).first()
            # Add the dish name.
            if dish.name in totals_dict['dishes']:
                # Add the amount.
                totals_dict['dishes'][dish.name] += 1
            # Otherwise.
            else:
                # Set the amount.
                totals_dict['dishes'][dish.name] = 1
            # Iterate through all the ingredients.
            for dish_ing in dish.dishingredient_set.all():
                # The ingredient's name.
                ingredient_name = dish_ing.ingredient.name
                # Append to the totals.
                if ingredient_name in totals_dict['ingredients']:
                    # Add the amount.
                    totals_dict['ingredients'][ingredient_name] += dish_ing.weight_in_grams
                # Otherwise.
                else:
                    # Set the amount.
                    totals_dict['ingredients'][ingredient_name] = dish_ing.weight_in_grams
        # Parse the information.
        context = {
            'schedule': [
                {
                    'name': menu.name,
                    'description': menu.description,
                    'ingredients': [
                        f"{dish_ing.ingredient.name} ({dish_ing.weight_in_grams * user_count}g)"
                        for
                        dish_ing in menu.dishingredient_set.all()
                    ]
                } for menu in [Dish.objects.filter(id=m_id).first() for m_id in meal_schedule['schedule'].values()]
            ],
            'products': [
                {
                    'name': product.ingredient.name,
                    'weight': product.ingredient_weight_in_grams,
                    'price': product.total_price,
                    'amount': p_amount,
                    'total_price': "{:0.2f}".format(float(p_amount * product.total_price)),
                    'total_weight':  "{:0.2f}".format(float(p_amount * product.ingredient_weight_in_grams)),
                    'total_price_f': float(p_amount * product.total_price),
                    'total_weight_f': float(p_amount * product.ingredient_weight_in_grams),
                }
                for
                product, p_amount in [
                    (Product.objects.filter(id=p_id).first(), p_amount)
                    for
                    p_id, p_amount in meal_schedule['products'].items()
                ]
                if
                p_amount > 0
            ],
            'total': {
                'dishes': [
                    f"{dish_name} (x{dish_amount})"
                    for
                    dish_name, dish_amount in totals_dict['dishes'].items()
                ],
                'ingredients': [
                    f"{ing_name} ({ing_weight * user_count}g)"
                    for
                    ing_name, ing_weight in totals_dict['ingredients'].items()
                ],
                'products': {}
            }
        }
        context['total']['products']['weight'] = "{:0.2f}".format(sum([product['total_weight_f'] for product in context['products']]))
        context['total']['products']['price'] = "{:0.2f}".format(sum([product['total_price_f'] for product in context['products']]))
        # Return the info.
        return context

    # Get all the valid search tasks.
    @staticmethod
    def getValidSearchTasks(plan_user) -> Iterable[Task]:
        for task in (
            Task.objects.filter(
                schedule__plan__sharing_status='PUBLIC',
                schedule__plan__plan_completion=True
            ) | Task.objects.filter(
                schedule__plan__sharing_status='PUBLIC_END',
                schedule__plan__plan_route__isnull=False,
                schedule__plan__plan_route__expected_end_date__isnull=False,
                schedule__plan__plan_route__expected_end_date__gt=datetime.now(),
                schedule__plan__plan_completion=True
            ) | Task.objects.filter(
                schedule__plan__in=plan_user.plan_set.all()
            )
        ).prefetch_related('schedule__plan__assigned_users').distinct():
            yield task
        return

    @staticmethod
    def obtainFullData(request, plan_user, current_user_access_level, plan):
        return {
            # The plan id.
            'plan': plan.id,
            # Check if the user is admin.
            'user_data': {
                # The user id.
                'id': request.user.id,
                # The user level.
                'level': current_user_access_level,
            },
            'search_data': {
                'tasks': [
                    {
                        'task_data': {
                            'name': task.name,
                            'display': task.display_name,
                            'description': task.task_description,
                            'extra_data': task.advanced_settings,
                        },
                        'plan_data': {
                            'id': task.schedule.plan.id,
                            'name': task.schedule.plan.name,
                            'description': task.schedule.plan.description,
                            'info': {
                                'team_count': task.schedule.plan.assigned_users.count(),
                                'shifts_count': task.schedule.total_shift_amount,
                            }
                        }
                    } for task in PlanOperations.getValidSearchTasks(plan_user)
                ]
            },
            # Send the plan fill data.
            'data': {
                # The general path.
                'route_path': {
                    'status': plan.plan_maker_progress['route_path'],
                    'content': PlanOperations.get_plan_route_path(plan)
                },
                # The general duration.
                'route_duration': {
                    'status': plan.plan_maker_progress['route_duration'],
                    'content': PlanOperations.get_plan_route_duration(plan)
                },
                # The general path.
                'general_info': {
                    'status': plan.plan_maker_progress['general_info'],
                    'content': {
                        'plan_name': plan.name,
                        'plan_description': plan.description,
                        'plan_sharing': plan.sharing_status
                    }
                },
                # The general team.
                'general_team': {
                    'status': plan.plan_maker_progress['general_team'],
                    'content': [{
                        # The user id.
                        'user_id': access.user.id,
                        # The username.
                        'username': access.user.username,
                        # The access level.
                        'level': access.level
                    } for access in PlanAccess.objects.filter(plan_id=plan.id)]
                },
                # The assignments' settings.
                'assignments_settings': {
                    'status': plan.plan_maker_progress['assignments_settings'],
                    'content': PlanOperations.get_plan_assignments_settings(plan)
                },
                # The assignments' tasks.
                'assignments_tasks': PlanOperations.get_plan_assignments_tasks(plan),
                # The assignments' settings.
                'assignments_options': {
                    'status': plan.plan_maker_progress['assignments_options'],
                    'content': None
                },
                # assignments' schedule.
                'assignments_schedule': {
                    'status': plan.plan_maker_progress['assignments_schedule'],
                    'content': PlanOperations.get_plan_assignments_schedule(plan),
                },
                # assignments' schedule.
                'meals_settings': {
                    'status': plan.plan_maker_progress['meals_settings'],
                    'content': PlanOperations.get_plan_meals_settings(plan),
                },
                # assignments' schedule.
                'meals_selection': {
                    'status': plan.plan_maker_progress['meals_selection'],
                    'content': PlanOperations.get_plan_meals_selection(plan),
                },
                # assignments' schedule.
                'meals_schedule': {
                    'status': plan.plan_maker_progress['meals_schedule'],
                    'content': PlanOperations.get_plan_meals_schedule(plan),
                }
            }
        }
