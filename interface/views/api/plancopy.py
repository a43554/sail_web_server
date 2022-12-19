from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from rest_framework.views import APIView

# The page for plan copying.
from main.models import Plan, PlanAccess
from nutrition.models import Menu
from routing.models import Route, Location, StopLocation
from scheduling.models import Schedule


class PlanCopier(LoginRequiredMixin, APIView):
    # The login url.
    login_url = '/login'

    # The POST method for this class.
    def post(self, request, plan_id: str):
        # Attempt to get the plan.
        source_plan = Plan.objects.filter(id=plan_id).first()
        # Check if plan can be accessed by this user.
        if not (
            request.user in source_plan.assigned_users.all()
            or
            (
                source_plan.plan_completion and source_plan.sharing_status == 'PUBLIC'
            )
            or
            (
                source_plan.sharing_status == 'PUBLIC_END'
                and
                source_plan.plan_route is not None
                and
                source_plan.plan_route.expected_end_date is not None
                and
                source_plan.plan_route.expected_end_date >= datetime.now()
            )
        ):
            # Raise the 403 exception.
            return HttpResponseForbidden(f'User \'{request.user.id}\' does not have permission to view this plan.')
        # Add each item to the access.
        with transaction.atomic():
            # Create a copy of the plan.
            new_plan = Plan(
                name=source_plan.name + " (Novo)",
                description=source_plan.description,
                sharing_status='PUBLIC_END',
                plan_maker_progress=dict([
                    (
                        key, Plan.DEFAULT_PROGRESS.get(key, 'LOCK')
                    ) for key in source_plan.plan_maker_progress.keys()
                ])
            )
            # Save the plan.
            new_plan.save()

            #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
            #   COPY ACCESS
            #
            # Add this user to the assigned users.
            PlanAccess(
                plan=new_plan,
                user=request.user,
                level=PlanAccess.OWNER,
            ).save()

            #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
            #   COPY ROUTE
            #
            # Copy the start location.
            new_start_location = source_plan.plan_route.start_location
            # Clear the key.
            new_start_location.pk = None
            # Save the model.
            new_start_location.save()

            # Copy the end location.
            new_end_location = source_plan.plan_route.end_location
            # Clear the key.
            new_end_location.pk = None
            # Save the model.
            new_end_location.save()

            # Create the new route.
            new_route = Route(
                start_location=new_start_location,
                end_location=new_end_location
            )
            # Save the route.
            new_route.save()

            # Setup all the stops.
            for stop in source_plan.plan_route.stoplocation_set.all():  # type: StopLocation
                # Obtain the matching location.
                new_location = stop.location
                # Clear the primary key.
                new_location.pk = None
                # Save the new location.
                new_location.save()

                # Clear the primary key.
                stop.pk = None
                # Update the stop.
                stop.location = new_location
                stop.route = new_route
                # Save the new stop.
                stop.save()

            #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
            #   COPY TASKS
            #
            # Create the new schedule.
            new_schedule = Schedule(
                total_shift_amount=source_plan.plan_schedule.total_shift_amount,
                total_shifts_per_day=source_plan.plan_schedule.total_shifts_per_day
            )
            # Save the schedule.
            new_schedule.save()
            # Dictionary to store incompatibility.
            incompatibility = {}
            # Iterate through every task.
            for task in source_plan.plan_schedule.tasks.all():
                # Obtain the original id.
                original_id = task.id
                # Obtain the incompatible tasks.
                incompatible_tasks = list(task.incompatible_person_tasks.all())

                # Clear the key.
                task.pk = None
                # Update the schedule.
                task.schedule = new_schedule
                # Save the task.
                task.save()

                # Check if this id is already on the dictionary.
                for task_to_mark in incompatibility[original_id] if original_id in incompatibility else []:
                    # Create the relationship.
                    task.incompatible_person_tasks.add(task_to_mark)

                # Iterate through the incompatible tasks.
                for other_task in incompatible_tasks:
                    # Obtain the content.
                    task_listing = incompatibility.setdefault(other_task.id, [])
                    # Add the new task to it.
                    task_listing.append(task)

            #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
            #   COPY MEALS
            #
            new_meal = Menu(
                name=source_plan.plan_meal.name,
                meal_times=source_plan.plan_meal.meal_times,
                last_solutions=source_plan.plan_meal.last_solutions,
            )
            # Save the menu.
            new_meal.save()
            # Iterate through every possible meal.
            for possible_meal in source_plan.plan_meal.possible_meals.all():
                # Add it to the new menu.
                new_meal.possible_meals.add(possible_meal)

            # Update the plan parts.
            new_plan.plan_route = new_route
            new_plan.plan_schedule = new_schedule
            new_plan.plan_meal = new_meal
            # Save the plan.
            new_plan.save()
        # Return the post id.
        return redirect(f'/plans/{new_plan.id}')
