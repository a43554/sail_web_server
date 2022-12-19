from datetime import datetime
from typing import Tuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Exists, OuterRef
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView


# The page for the list of plans.
from main.models import Plan, PlanAccess
from system.models import Client


class PlanListPage(LoginRequiredMixin, APIView):
    # The class used for rendering.
    renderer_classes = [TemplateHTMLRenderer]
    # The template's name.
    template_name = 'demos/main/plan/list/plan_selection.html'
    # The login url.
    login_url = '/login'

    # The GET method for this class.
    def get(self, request):
        # Get the user.
        user: Client = request.user
        # Get all plans where this user takes part in.
        plan_query = (
            user.plan_set.all()
            |
            Plan.objects.filter(sharing_status='PUBLIC', plan_completion=True)
            |
            Plan.objects.filter(
                sharing_status='PUBLIC_END',
                plan_route__isnull=False,
                plan_route__expected_end_date__isnull=False,
                plan_route__expected_end_date__lt=datetime.now(),
                plan_completion=True
            )
        ).distinct()
        # The list of all plans.
        parsed_plans = []
        # Construct an array of plan data.
        for idx, plan in enumerate(plan_query):  # type: int, Plan
            # Construct a json of data.
            parsed_plans.append({
                'id': plan.id,
                'profile_image': (plan.id % 8) + 1,
                'is_participant': user.plan_set.filter(id=plan.id).filter().first() is not None,
                'is_complete': plan.plan_completion,
                'name': plan.name,
                'description': plan.description,
                'info': {
                    'team_count': plan.assigned_users.count(),
                    'meals_count': len(plan.plan_meal.meal_times) if plan.plan_meal is not None else '-',
                    'shifts_count': plan.plan_schedule.total_shift_amount if plan.plan_schedule is not None else '-',
                }
            })
        # Return the response with the html content.
        return Response({
            'plans': parsed_plans
        })
