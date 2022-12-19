import math
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound, HttpResponseForbidden
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from interface.views.api.utils_plan_operations import PlanOperations
from main.models import PlanAccess
from main.models.PlanModel import Plan
from routing.models import StopLocation


# The page for displaying a schedule.
class PlanStartPage(LoginRequiredMixin, APIView):
    # The class used for rendering.
    renderer_classes = [TemplateHTMLRenderer]
    # The template's name.
    template_name = 'demos/main/plan/plans/start_page.html'
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
        # Obtain the access.
        access = PlanAccess.objects.filter(plan_id=plan_id, user_id=request.user.id).first()
        # Get the current plan's end date, if one exists.
        plan_finish_date = plan.plan_route.expected_end_date if plan.plan_route is not None else None
        # Check if user doesn't have access.
        if (
            access is None
            and
            (
                plan.sharing_status == 'PRIVATE'
                or
                (
                    plan.sharing_status == 'PUBLIC_END'
                    and
                    (
                        plan_finish_date is None
                        or
                        plan_finish_date.date() >= datetime.utcnow().date()
                    )
                )
            )
        ):
            # Raise the 403 exception.
            return HttpResponseForbidden(f'User \'{request.user.id}\' does not have permission to view this plan.')
        # Obtain the access level.
        access_level = access.level if access is not None else PlanAccess.USER
        # Map the context.
        context = PlanOperations.obtainFullData(request, request.user, access_level, plan)
        # Return the response with the html content.
        return Response(context)
