import json
from datetime import datetime
from math import isfinite
from typing import Dict, Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from rest_framework.views import APIView

from interface.views.api.utils_plan_operations import PlanOperations
from interface.views.api.utils_progress_operations import ProgressOperations
from main.models import Plan, PlanAccess
from nutrition.models import Menu, Dish
from routing.models import Route, Location, StopLocation
from scheduling.models import Task
from scheduling.models.ScheduleModel import Schedule
from system.models import Client
from utils.exceptions import FormErrorException, WarningException

# The page for plan making.
from utils.new.ScheduleOptions import ScheduleOptions


class PlanMaker(LoginRequiredMixin, APIView):
    # The login url.
    login_url = '/login'

    # Validate the general team.
    def validate_general_info(self, input_data: dict, plan: Plan, ):
        # Check if both dates are present.
        if 'general_info_plan_name' not in input_data or 'general_info_plan_description' not in input_data:
            # Raise an error.
            raise KeyError("MISSING_NAME_OR_DESCRIPTION")
        # Save the data.
        plan.name = input_data['general_info_plan_name']
        plan.description = input_data['general_info_plan_description']
        # Check if share status is one of the possible ones.
        if input_data['plan_share_status'] in ['PUBLIC', 'PRIVATE', 'PUBLIC_END']:
            # Set the value.
            plan.sharing_status = input_data['plan_share_status']
        # Update the status.
        ProgressOperations.complete_section(
            'general_info', plan.plan_maker_progress
        )
        # Save the model.
        plan.save()

    # Validate the general team.
    def validate_general_team(self, input_data: dict, plan: Plan, user_access: PlanAccess):
        # Store it in a dictionary.
        aux_dict: Dict[str, Any] = {}
        # Loop to fil the array.
        for k, v in input_data.items():
            # Obtain the key.
            split_formatted_key = k.split('_')
            # Store the results.
            key_type, key_number = split_formatted_key[0], split_formatted_key[1]
            # Check to see if the key is of id.
            if key_type == 'userid':
                # Add to the dictionary.
                aux_dict.setdefault(key_number, {'username': None, 'admin': False, 'error': None})['username'] = v
            # Check to see if the key is of admin.
            elif key_type == 'useradmin':
                # Add to the dictionary.
                aux_dict.setdefault(key_number, {'username': None, 'admin': False, 'error': None})['admin'] = True
        # Add each item to the access.
        with transaction.atomic():
            # Valid items.
            next_selection = []
            # Previous selection.
            previous_selection = [str(i) for i in plan.assigned_users.values_list('id', flat=True)]
            # Iterate though all the results.
            for key_number, user_dict in aux_dict.items():
                # Obtain the user id and admin status.
                username, is_admin = user_dict['username'], user_dict['admin']
                # Check if id exists.
                if username is None:
                    # Mark it as error.
                    raise Exception("Campo de nome de utilizador não pode estar vazio.")
                # Obtain the client.
                client = Client.objects.filter(username=username).first()
                # Check if user exists in the database.
                if client is None:
                    # Mark it as error.
                    raise Exception(f"Utilizador \'{username}\' não encontrado.")
                # Obtain the access.
                access = PlanAccess.objects.filter(user_id=client.id, plan_id=plan.id).first()
                # Check if access already exists.
                if access is not None:
                    # Check if modified access is of user.
                    if access.level == access.USER:
                        # Check if any changes occurred.
                        if is_admin:
                            # Modify the access.
                            access.level = PlanAccess.ADMIN if is_admin else PlanAccess.USER
                            # Save the changes.
                            access.save()
                    # Check if modified access is of admin.
                    elif access.level == access.ADMIN:
                        # Check if any changes occurred.
                        if not is_admin:
                            # Only owner can change admin status
                            if user_access.level != PlanAccess.OWNER:
                                # Mark it as error.
                                raise Exception(f"Utilizador não tem permissão suficiente.")
                            # Modify the access.
                            access.level = PlanAccess.USER
                            # Save the changes.
                            access.save()
                # If access does not exist.
                else:
                    # Add the new access.
                    PlanAccess(
                        plan_id=plan.id,
                        user_id=client.id,
                        level=PlanAccess.ADMIN if is_admin else PlanAccess.USER
                    ).save()
                # Store the id as valid.
                next_selection.append(str(client.id))
            # Check which access have been removed.
            removed_accesses = list(set(previous_selection).difference(next_selection))
            # Iterate though the removed accesses.
            for removed_id in removed_accesses:
                # Obtain the access.
                access = PlanAccess.objects.filter(user_id=removed_id, plan_id=plan.id).first()
                # Check if it exists.
                if access is None:
                    # Raise exception.
                    raise Exception("Invalid plan or user id.")
                # Check if to be deleted account level is owner.
                if access.level == PlanAccess.OWNER:
                    # Cannot remove owner.
                    raise Exception("Cannot remove owner.")
                # Check if to be deleted account level is admin.
                elif access.level == PlanAccess.ADMIN:
                    # Check if user performing action is not owner.
                    if user_access.level != PlanAccess.OWNER:
                        # Admin cannot remove owner.
                        raise Exception("Only owner can remove admins.")
                # Delete the access.
                access.delete()
            # Check if any error occurred.
            if any(user_dict['error'] is not None for user_dict in aux_dict.values()):
                # Raise an exception.
                raise FormErrorException(aux_dict)
            # Update the status.
            ProgressOperations.complete_section(
                'general_team', plan.plan_maker_progress
            )
            # Save the model.
            plan.save()

    # Validate the route path.
    def validate_route_path(self, input_data: dict, plan: Plan):
        # Store the split variables.
        aux_dict = {}
        # A minimum of 2 items should be in the input data.
        if len(input_data) < 2:
            # Raise exception.
            raise KeyError("INVALID_PATH")
        # Loop to fil the array.
        for k, v in input_data.items():
            # Key must be either lat or long.
            formatted_key = k.split('_')[0]
            # Surround with catch.
            try:
                # Transform the value into a float.
                float_v = float(v)
            # Catch any exceptions.
            except:
                # Raise an exception.
                raise ValueError("INVALID_VALUE")
            # Check for validity.
            if formatted_key == 'lat':
                # Validate latitude.
                if not (isfinite(float_v) and abs(float_v) <= 90):
                    # Raise an exception.
                    raise ValueError("INVALID_LATITUDE")
            elif formatted_key == 'long':
                # Validate longitude.
                if not (isfinite(float_v) and abs(float_v) <= 180):
                    # Raise an exception.
                    raise ValueError("INVALID_LONGITUDE")
            else:
                # Raise an exception.
                raise KeyError("LATITUDE_LONGITUDE_REQUIRED")
            # Append to the dictionary.
            aux_dict.setdefault(k.split('_')[-1], {})[k.split('_')[0]] = float_v
        # Make sure all contain both lat and long.
        if any(res_dict for res_dict in aux_dict.values() if ('lat' not in res_dict or 'long' not in res_dict)):
            # Raise an exception.
            raise KeyError("LATITUDE_LONGITUDE_REQUIRED")
        # Obtain the start value.
        result_dictionary = {
            'start': aux_dict['0'],
            'finish': aux_dict['-1'],
        }
        # Remove non path values.
        del aux_dict['0']
        del aux_dict['-1']
        # Store the resulting path.
        result_dictionary['stops'] = list(aux_dict.values())
        # Add each item to the access.
        with transaction.atomic():
            # Delete the previous route.
            plan_route = plan.plan_route
            # Check if it doesn't exist.
            if plan_route is None:
                # Create the route.
                plan_route = Route()
                # Save the route
                plan_route.save()
                # Set the plan's route.
                plan.plan_route = plan_route
            # Check if it does exist.
            if plan_route.start_location is not None:
                # Delete it.
                plan_route.start_location.delete()
            # Create it.
            start_location = Location(
                latitude=result_dictionary['start']['lat'],
                longitude=result_dictionary['start']['long']
            )
            # Save it.
            start_location.save()
            # Update the plan route.
            plan_route.start_location = start_location

            # Check if it does exist.
            if plan_route.end_location is not None:
                # Delete it.
                plan_route.end_location.delete()
            # Create it.
            end_location = Location(
                latitude=result_dictionary['finish']['lat'],
                longitude=result_dictionary['finish']['long']
            )
            # Save it.
            end_location.save()
            # Update the plan route.
            plan_route.end_location = end_location

            # Delete all stop locations.
            [stop_location.delete() for stop_location in plan_route.stop_locations.all()]

            # Add all the new stop locations.
            for idx, stop_data in enumerate(result_dictionary['stops']):
                # Add all stops.
                curr_loc = Location(latitude=stop_data['lat'], longitude=stop_data['long'])
                # Save the new location
                curr_loc.save()
                # Create the connection.
                stop_loc = StopLocation(location=curr_loc, route=plan_route, order=idx+1)
                # Save the stop location.
                stop_loc.save()
            # Update the status.
            ProgressOperations.complete_section(
                'route_path', plan.plan_maker_progress,
            )
            # Save the route
            plan_route.save()
            # Save the model.
            plan.save()

    # Validate the route duration.
    def validate_route_duration(self, input_data: dict, plan: Plan):
        # Check if both dates are present.
        if 'route_duration_start' not in input_data or 'route_duration_finish' not in input_data:
            # Raise an error.
            raise KeyError("MISSING_START_OR_FINISH_TIMES")
        # Create a dictionary to store the results.
        result_dictionary = {
            'start': input_data['route_duration_start'],
            'finish': input_data['route_duration_finish'],
        }
        # Check if the dates are valid.
        start_time = datetime.strptime(result_dictionary['start'], '%d/%m/%Y')
        finish_time = datetime.strptime(result_dictionary['finish'], '%d/%m/%Y')
        # Check if the dates are valid.
        if start_time > finish_time:
            # Invalid date raise an exception.
            raise ValueError("START_DATE_MUST_NOT_BE_AFTER_END_DATE")
        # Add each item to the access.
        with transaction.atomic():
            # Delete the previous route.
            plan_route = plan.plan_route
            # Check if it doesn't exist.
            if plan_route is None:
                # Create the route.
                plan_route = Route()
                # Save the route
                plan_route.save()
                # Set the plan's route.
                plan.plan_route = plan_route
            # Update the start and end times.
            plan.plan_route.expected_start_date = start_time
            plan.plan_route.expected_end_date = finish_time
            # Update the status.
            ProgressOperations.complete_section(
                'route_duration', plan.plan_maker_progress
            )
            # Save the route
            plan_route.save()
            # Save the model.
            plan.save()

    # Validate the assignments settings.
    def validate_assignments_settings(self, input_data: dict, plan: Plan):
        # Check if both dates are present.
        if 'assignments_total_days' not in input_data or 'assignments_turns_per_day' not in input_data:
            # Raise an error.
            raise KeyError("MISSING_TOTAL_SHIFTS_OR_DAILY_SHIFTS")
        # Surround with catch.
        try:
            # Transform the value into a float.
            total_days = int(input_data['assignments_total_days'])
        # Catch any exceptions.
        except:
            # Raise an exception.
            raise ValueError("INVALID_TOTAL_SHIFTS_VALUE")
        # Surround with catch.
        try:
            # Transform the value into a float.
            daily_shifts = int(input_data['assignments_turns_per_day'])
        # Catch any exceptions.
        except:
            # Raise an exception.
            raise ValueError("INVALID_SHIFTS_PER_DAY_VALUE")
        # Add each item to the access.
        with transaction.atomic():
            # Delete the previous route.
            plan_schedule = plan.plan_schedule
            # Check if it doesn't exist.
            if plan_schedule is None:
                # Create the route.
                plan_schedule = Schedule()
                # Set the plan schedule.
                plan.plan_schedule = plan_schedule
            # Update the start and end times.
            plan.plan_schedule.total_shift_amount = total_days * daily_shifts
            plan.plan_schedule.total_shifts_per_day = daily_shifts
            # Update the status.
            ProgressOperations.complete_section(
                'assignments_settings', plan.plan_maker_progress,
            )
            # Save the route
            plan_schedule.save()
            # Save the model.
            plan.save()

    # Validate the assignments tasks.
    def validate_assignments_tasks(self, input_data: dict, plan: Plan):
        # Check if the id is present.
        if (
                ('task_number' not in input_data)
        ):
            # Raise an error.
            raise KeyError("MISSING_FIELDS")
        # The task id number.
        task_id_number = input_data["task_number"].replace('Tarefa ', '')
        # Task full id.
        task_full_id = 'assignments_tasks_' + task_id_number
        # Add each item to the access.
        with transaction.atomic():
            # Get the task with this id, if any exists.
            task = plan.plan_schedule.tasks.filter(name=task_full_id).first()
            # Obtain the schedule.
            schedule = plan.plan_schedule
            # Check if task exists.
            if task is None:
                # Create a new task.
                task = Task(schedule=schedule)
                # Save the task.
                task.save()

            # Set the name.
            task.name = task_full_id

            # Check if both dates are present.
            if 'task_name' not in input_data or 'task_description' not in input_data:
                # Raise an error.
                raise KeyError("MISSING_FIELDS")
            # Otherwise.
            else:
                # Set the name and description.
                task.display_name = input_data['task_name']
                task.task_description = input_data['task_description']

            # Check if both dates are present.
            if f'task_{task_id_number}_max_people_present_in_each_slot' not in input_data or f'task_{task_id_number}_min_people_present_in_each_slot' not in input_data:
                # Raise an error.
                raise KeyError("MISSING_FIELDS")
            # Otherwise.
            else:
                # Check if both values are ints.
                try:
                    max_people_per_slot = int(input_data[f'task_{task_id_number}_max_people_present_in_each_slot'])
                    min_people_per_slot = int(input_data[f'task_{task_id_number}_min_people_present_in_each_slot'])
                    # Check if both are larger than one and each or more to one other.
                    if max_people_per_slot < min_people_per_slot:
                        # Invalid date raise an exception.
                        raise ValueError("INVALID_PERSON_CYCLE_VALUES")
                except:
                    raise ValueError("INVALID_PERSON_CYCLE_VALUES")
                # Set the name and description.
                task.advanced_settings['people_per_shift_task'] = {
                    "setting_type": ScheduleOptions.DATA,
                    "setting_value": {
                        "max_amount": max_people_per_slot,
                        "min_amount": min_people_per_slot,
                    }
                }

            # Check if both dates are present.
            if (
                    (f'task_{task_id_number}_per_person_cycle_settings_switch' not in input_data)
                    or
                    (input_data[f'task_{task_id_number}_per_person_cycle_settings_switch'] != 'on')
            ):
                # Set the name and description.
                task.advanced_settings['per_person_cycle_settings'] = {
                    "setting_type": ScheduleOptions.SETTING,
                    "setting_value": ScheduleOptions.NONE
                }
            # If other fields not present.
            elif (
                    (f'task_{task_id_number}_per_person_cycle_settings_options_cycle' not in input_data) or
                    (f'task_{task_id_number}_per_person_cycle_settings_options_target' not in input_data)
            ):
                # Raise an error.
                raise KeyError("MISSING_FIELDS")
            # Otherwise.
            else:
                # Check if both values are ints.
                try:
                    person_cycle_options_cycle = int(input_data[f'task_{task_id_number}_per_person_cycle_settings_options_cycle'])
                    person_cycle_options_target = int(input_data[f'task_{task_id_number}_per_person_cycle_settings_options_target'])
                    # Check if both are larger than one and each or more to one other.
                    if (
                            (person_cycle_options_target > person_cycle_options_cycle) or
                            (person_cycle_options_cycle < 0) or
                            (person_cycle_options_target < 0)
                    ):
                        # Invalid date raise an exception.
                        raise ValueError("INVALID_PERSON_CYCLE_VALUES")
                except:
                    raise ValueError("INVALID_PERSON_CYCLE_VALUES")
                # Set the name and description.
                task.advanced_settings['per_person_cycle_settings'] = {
                    "setting_type": ScheduleOptions.DATA,
                    "setting_value": {
                        "total_shifts_per_cycle": person_cycle_options_cycle,
                        "assigned_shifts_per_cycle": person_cycle_options_target,
                    }
                }

            # Check if both dates are present.
            if (
                    (f'task_{task_id_number}_per_task_cycle_settings_switch' not in input_data)
                    or
                    (input_data[f'task_{task_id_number}_per_task_cycle_settings_switch'] != "on")
            ):
                # Set the name and description.
                task.advanced_settings['per_task_cycle_settings'] = {
                    "setting_type": ScheduleOptions.SETTING,
                    "setting_value": ScheduleOptions.NONE
                }
            # If other fields not present.
            elif (
                    (f'task_{task_id_number}_per_task_cycle_settings_options_cycle' not in input_data) or
                    (f'task_{task_id_number}_per_task_cycle_settings_options_target' not in input_data)
            ):
                # Raise an error.
                raise KeyError("MISSING_FIELDS")
            # Otherwise.
            else:
                # Check if both values are ints.
                try:
                    task_cycle_options_cycle = int(input_data[f'task_{task_id_number}_per_task_cycle_settings_options_cycle'])
                    task_cycle_options_target = int(input_data[f'task_{task_id_number}_per_task_cycle_settings_options_target'])
                    # Check if both are larger than one and each or more to one other.
                    if (
                            (task_cycle_options_cycle < task_cycle_options_target) or
                            (task_cycle_options_cycle < 0) or
                            (task_cycle_options_target < 0)
                    ):
                        # Invalid date raise an exception.
                        raise ValueError("INVALID_TASK_CYCLE_VALUES")
                except:
                    raise ValueError("INVALID_TASK_CYCLE_VALUES")
                # Set the name and description.
                task.advanced_settings['per_task_cycle_settings'] = {
                    "setting_type": ScheduleOptions.DATA,
                    "setting_value": {
                        "total_shifts_per_cycle": task_cycle_options_cycle,
                        "assigned_shifts_per_cycle": task_cycle_options_target,
                    }
                }

            # Check if both dates are present.
            if (
                    (f'task_{task_id_number}_sequential_settings_switch' not in input_data)
                    or
                    (input_data[f'task_{task_id_number}_sequential_settings_switch'] != "on")
            ):
                # Set the name and description.
                task.advanced_settings['sequential_settings'] = {
                    "setting_type": ScheduleOptions.SETTING,
                    "setting_value": ScheduleOptions.NONE
                }
            # If other fields not present.
            elif (
                    (f'task_{task_id_number}_sequential_settings_total_shifts' not in input_data)
            ):
                # Raise an error.
                raise KeyError("MISSING_FIELDS")
            # Otherwise.
            else:
                # Check if both values are ints.
                try:
                    sequential_settings_total_shifts = int(input_data[f'task_{task_id_number}_sequential_settings_total_shifts'])
                    diversify_cast_switch = (
                        f'task_{task_id_number}_diversify_cast_switch' in input_data and input_data[f'task_{task_id_number}_diversify_cast_switch'] == 'on'
                    )
                    # Check if both are larger than one and each or more to one other.
                    if sequential_settings_total_shifts < 0:
                        # Invalid date raise an exception.
                        raise ValueError("INVALID_CAST_VALUES")
                except:
                    raise ValueError("INVALID_CAST_VALUES")
                # Set the name and description.
                task.advanced_settings['sequential_settings'] = {
                    "setting_type": "DATA",
                    "setting_value": {
                        "diversify_cast": diversify_cast_switch,
                        "number_of_sequential_shifts": sequential_settings_total_shifts
                    }
                }

            # Set the name and description.
            task.advanced_settings['valid_shifts'] = {
                "setting_type": ScheduleOptions.DATA,
                "setting_value": sorted([
                    ((int(pair[0]) - 1) * plan.plan_schedule.total_shifts_per_day) + (int(pair[1]) - 1)
                    for pair in [
                        key.split('_')[-2:]
                        for key, value in input_data.items()
                        if key.startswith(f"task_{task_id_number}_valid_shift_input_") and value == 'on'
                    ]
                ])
            }

            # Update the status.
            ProgressOperations.complete_section(
                task_full_id,
                plan.plan_maker_progress,
            )
            # Save the task.
            task.save()
            # Save the model.
            plan.save()

    # Validate the assignments tasks.
    def validate_assignments_options(self, input_data: dict, plan: Plan):
        # Add each item to the access.
        with transaction.atomic():
            # Iterate through all tasks.
            for task_1 in plan.plan_schedule.tasks.all():
                # Clear the incompatible tasks.
                task_1.incompatible_person_tasks.clear()
                # Clear the incompatible people.
                task_1.qualified_members.clear()
                # Iterate through all tasks.
                for task_2 in plan.plan_schedule.tasks.all():
                    # Skip equal tasks.
                    if task_1.name == task_2.name:
                        # Continue.
                        continue
                    # Construct the key.
                    expected_key = f'incompatible_tasks__{task_1.name}__{task_2.name}'
                    # Check if the key isn't contained in the input data.
                    if expected_key not in input_data or input_data[expected_key] != 'on':
                        # Add it to the incompatible task list.
                        task_1.incompatible_person_tasks.add(task_2)
                # Iterate through all users in the plan.
                for member in plan.assigned_users.all():
                    # Construct the key.
                    expected_key = f'incompatible_team__{task_1.name}__{member.id}'
                    # Check if the key isn't contained in the input data.
                    if expected_key in input_data and input_data[expected_key] == 'on':
                        # Add it to the incompatible task list.
                        task_1.qualified_members.add(member)
                # Save the task.
                task_1.save()
            # Update the status.
            ProgressOperations.complete_section(
                'assignments_options',
                plan.plan_maker_progress,
            )
            # Create the parser.
            plan.plan_schedule.reload_schedule()
            # Check if the plan schedule generated was a success.
            if len(plan.plan_schedule.last_solutions) == 0 and plan.plan_schedule.tasks.count() > 0:
                # Raise an exception.
                raise WarningException("Não foi possível gerar um plano de tarefas que garanta o cumprimento das condições de todas as tarefas, por favor ajuste as tarefas de forma a evitar incompatibilidades.")
            # Save the model.
            plan.save()

    # Validate the assignments tasks.
    def validate_assignments_schedule(self, input_data: dict, plan: Plan):
        # Add each item to the access.
        with transaction.atomic():
            # Update the status.
            ProgressOperations.complete_section(
                'assignments_schedule',
                plan.plan_maker_progress,
            )
            # Save the model.
            plan.save()

    # Validate the assignments tasks.
    def validate_meals_settings(self, input_data: dict, plan: Plan):
        # Store it in a dictionary.
        aux_dict: Dict[str, Any] = {}
        # Loop to fil the array.
        for k, v in input_data.items():
            # Obtain the key.
            split_formatted_key = k.replace('meal_time_', '').split('_input_type_')
            # Check if split length is 2.
            if len(split_formatted_key) != 2:
                # Ignore.
                continue
            # Store the results.
            meal_number, meal_type = split_formatted_key[0], split_formatted_key[1]
            # Check the meal type.
            if meal_type == '1':
                # Add to the dictionary.
                aux_dict.setdefault(meal_number, []).append('BREAKFAST')
            # Check the meal type.
            elif meal_type == '2':
                # Add to the dictionary.
                aux_dict.setdefault(meal_number, []).append('LUNCH')
            # Check the meal type.
            elif meal_type == '3':
                # Add to the dictionary.
                aux_dict.setdefault(meal_number, []).append('DINNER')
        # Transform the dictionary into a list.
        list_of_meal_times = [aux_dict[key] for key in sorted(aux_dict.keys())]
        # Add each item to the access.
        with transaction.atomic():
            # Delete the previous route.
            plan_meal = plan.plan_meal
            # Check if it doesn't exist.
            if plan_meal is None:
                # Create the menu.
                plan_meal = Menu()
                # Set the plan meal.
                plan.plan_meal = plan_meal
            # Check if share status is one of the possible ones.
            if input_data['meal_settings_priority'] in ['NONE', 'WEIGHT', 'PRICE']:
                # Set the value.
                plan_meal.product_priority = input_data['meal_settings_priority']
            # Set the meal times.
            plan_meal.meal_times = list_of_meal_times
            # Update the status.
            ProgressOperations.complete_section(
                'meals_settings',
                plan.plan_maker_progress,
            )
            # Save the plan meal.
            plan_meal.save()
            # Save the model.
            plan.save()

    # Validate the assignments tasks.
    def validate_meals_selection(self, input_data: dict, plan: Plan):
        # Add each item to the access.
        with transaction.atomic():
            # Select the meal plan.
            plan_meal = plan.plan_meal
            # Clear the possible meals list.
            plan_meal.possible_meals.clear()
            # Iterate through each dish.
            for dish_str in input_data.keys():  # type: str
                # Check if is of dish selection.
                if dish_str.startswith('dish_selection_'):
                    # Obtain the id.
                    dish_id = int(dish_str.replace('dish_selection_', ''))
                    # Add the dish to the list of possible dishes.
                    plan_meal.possible_meals.add(Dish.objects.filter(id=dish_id).first())
            # Construct the schedule.
            plan_meal.generate_schedule()
            # Update the status.
            ProgressOperations.complete_section(
                'meals_selection',
                plan.plan_maker_progress,
            )
            # Save the plan meal.
            plan_meal.save()
            # Save the model.
            plan.save()

    # Validate the assignments tasks.
    def validate_meals_schedule(self, input_data: dict, plan: Plan):
        # Add each item to the access.
        with transaction.atomic():
            # Update the status.
            ProgressOperations.complete_section(
                'meals_schedule',
                plan.plan_maker_progress,
            )
            # Save the model.
            plan.save()

    # The POST method for this class.
    def post(self, request, plan_id: str):
        # Attempt to get the plan.
        plan = Plan.objects.filter(id=plan_id).first()
        # Check if no plan was found.
        if plan is None:
            # Raise the 404 exception.
            return HttpResponseNotFound(f'No plan with ID \'{plan_id}\' was found.')
        # Obtain the access.
        access = PlanAccess.objects.filter(plan_id=plan_id, user_id=request.user.id).first()
        # Check if user doesn't have access.
        if access is None:
            # Raise the 403 exception.
            return HttpResponseForbidden(f'User \'{request.user.id}\' does not have permission to view this plan.')
        # Check if user doesn't have admin access.
        if access.level == PlanAccess.USER:
            # Raise the 403 exception.
            return HttpResponseForbidden(f'User \'{request.user.id}\' does not have permissions to modify this plan.')
        # Load the data into a json object.
        json_data = json.loads(request.data['data'])
        # Obtain the section.
        section = json_data['section']
        # Surround with try.
        try:
            # Check to see if the requirements are meet.
            if ProgressOperations.is_status_progress_from_target_str(
                    section,
                    plan.plan_maker_progress,
                    Plan.LOCK
            ):
                # Raise an error.
                return HttpResponseBadRequest(f'Please finish other sections before the current one.')
        # Catch any exceptions.
        except:
            # Raise an error.
            return HttpResponseBadRequest(f'Invalid plan section.')
        # The response to send.
        response_data, code = plan.plan_maker_progress, 200
        warning_data = None
        # Surround with try.
        try:
            # Check the type.
            if ProgressOperations.are_sections_equal(section, 'general_info', plan.plan_maker_progress):
                # Validate and process the data.
                self.validate_general_info(json_data['content'], plan)
            # Check the type.
            elif ProgressOperations.are_sections_equal(section, 'general_team', plan.plan_maker_progress):
                # Validate and process the data.
                self.validate_general_team(json_data['content'], plan, access)
            # Check the type.
            elif ProgressOperations.are_sections_equal(section, 'route_path', plan.plan_maker_progress):
                # Validate and process the data.
                self.validate_route_path(json_data['content'], plan)
            # Check the type.
            elif ProgressOperations.are_sections_equal(section, 'route_duration', plan.plan_maker_progress):
                # Validate and process the data.
                self.validate_route_duration(json_data['content'], plan)
            # Check the type.
            elif ProgressOperations.are_sections_equal(section, 'assignments_settings', plan.plan_maker_progress):
                # Validate and process the data.
                self.validate_assignments_settings(json_data['content'], plan)
            # Check the type.
            elif ProgressOperations.are_sections_equal(section, 'assignments_tasks_*', plan.plan_maker_progress):
                # Validate and process the data.
                self.validate_assignments_tasks(json_data['content'], plan)
            # Check the type.
            elif ProgressOperations.are_sections_equal(section, 'assignments_options', plan.plan_maker_progress):
                # Validate and process the data.
                self.validate_assignments_options(json_data['content'], plan)
            elif ProgressOperations.are_sections_equal(section, 'assignments_schedule', plan.plan_maker_progress):
                # Validate and process the data.
                self.validate_assignments_schedule(json_data['content'], plan)
            # Check the type.
            elif ProgressOperations.are_sections_equal(section, 'meals_settings', plan.plan_maker_progress):
                # Validate and process the data.
                self.validate_meals_settings(json_data['content'], plan)
            # Check the type.
            elif ProgressOperations.are_sections_equal(section, 'meals_selection', plan.plan_maker_progress):
                # Validate and process the data.
                self.validate_meals_selection(json_data['content'], plan)
            # Check the type.
            elif ProgressOperations.are_sections_equal(section, 'meals_schedule', plan.plan_maker_progress):
                # Validate and process the data.
                self.validate_meals_schedule(json_data['content'], plan)
        # Catch all exception form errors.
        except FormErrorException as e:
            # Obtain the json data.
            json_errors = e.exception_data
            # Return the request.
            response_data, code = json_errors, 400
        # Catch warnings.
        except WarningException as e:
            # Return the request.
            warning_data, code = str(e), 400
        # Catch all regular exceptions.
        except Exception as e:
            # Return the request.
            response_data, code = str(e), 400
        # Redirect to home.
        return JsonResponse({
            'errors': response_data,
            'warnings': warning_data,
            'progress_status': plan.plan_maker_progress,
            'context': PlanOperations.obtainFullData(request, request.user, access.level, plan)
        }, status=code)
