import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from rest_framework.views import APIView

from interface.views.api.utils_progress_operations import ProgressOperations
from main.models import Plan, PlanAccess


# The page for plan making.
class PlanMakerEdit(LoginRequiredMixin, APIView):
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
            # Check to see if the requirements are meet.
            if ProgressOperations.is_status_progress_from_target_str(
                    section, plan.plan_maker_progress, Plan.LOCK
            ):
                # Raise an error.
                return HttpResponseBadRequest(f'Please finish other sections before the current one.')
        # Catch any exceptions.
        except:
            # Raise an error.
            return HttpResponseBadRequest(f'Invalid plan section.')
        # The response to send.
        response_data, code = plan.plan_maker_progress, 200
        # Update the status.
        ProgressOperations.unlock_section(
            section,
            plan.plan_maker_progress,
        )
        # Save the plan.
        plan.save()
        # Redirect to home.
        return JsonResponse({
            'errors': response_data,
            'progress_status': plan.plan_maker_progress,
        }, status=code)
