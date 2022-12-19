import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from rest_framework.views import APIView

from interface.views.api.utils_plan_operations import PlanOperations
from interface.views.api.utils_progress_operations import ProgressOperations
from main.models import Plan, PlanAccess


# The page for plan making.
from scheduling.models import Task


class PlanMakerSwitchTask(LoginRequiredMixin, APIView):
    # The login url.
    login_url = '/login'

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
            # Check if it's of the correct type.
            if section in plan.plan_maker_progress:
                # Select the task.
                selected_task = plan.plan_schedule.tasks.filter(name=section).first()
                # Check if the task exists.
                if selected_task is not None:
                    # Delete it.
                    selected_task.delete()
                # Update the status.
                ProgressOperations.complete_section(
                    section,
                    plan.plan_maker_progress,
                )
                # Remove from the plan maker.
                del plan.plan_maker_progress[section]
                # Clear the current solution setup.
                plan.plan_schedule.last_solutions = {}
            # Add it to the task data.
            else:
                # Add the task.
                task = Task(
                    name=section,
                    display_name=f"Tarefa {section.split('_')[-1]}",
                    task_description='',
                    schedule=plan.plan_schedule,
                    advanced_settings={
                        "valid_shifts": {
                            "setting_type": "DATA",
                            "setting_value": [i for i in range(plan.plan_schedule.total_shift_amount)]
                        },
                        "sequential_settings": {
                            "setting_type": "SETTING",
                            "setting_value": None
                        },
                        "people_per_shift_task": {
                            "setting_type": "DATA",
                            "setting_value": {
                                "max_amount": '',
                                "min_amount": ''
                            }
                        },
                        "per_task_cycle_settings": {
                            "setting_type": "SETTING",
                            "setting_value": None
                        },
                        "per_person_cycle_settings": {
                            "setting_type": "SETTING",
                            "setting_value": None
                        }
                    }
                )
                # Save the task.
                task.save()
                # Clear the current solution setup.
                plan.plan_schedule.last_solutions = {}
                # Remove from the plan maker.
                plan.plan_maker_progress[section] = Plan.TODO
                # Update the status.
                ProgressOperations.unlock_section(
                    section,
                    plan.plan_maker_progress,
                )
        # Catch any exceptions.
        except:
            # Raise an error.
            return HttpResponseBadRequest(f'Invalid plan section.')
        # The response to send.
        response_data, code = plan.plan_maker_progress, 200
        # Save the schedule change.
        plan.plan_schedule.save()
        # Save the plan.
        plan.save()
        # Redirect to home.
        return JsonResponse({
            'errors': response_data,
            'progress_status': plan.plan_maker_progress,
            'context': PlanOperations.obtainFullData(request, request.user, access.level, plan)
        }, status=code)
