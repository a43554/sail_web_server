from rest_framework.response import Response
from rest_framework.views import APIView

from interface.views.api.utils_plan_operations import PlanOperations
from system.models import Client
from utils.auth.bearer import BearerAuthentication


# The login application view.
class MobilePlanInformationView(APIView):
    # The authentication classes.
    authentication_classes = [BearerAuthentication]

    # The "GET" method for this view.
    def get(self, request, plan_id):
        # Obtain the user.
        current_user: Client = request.user
        # Obtain the user's selected plans.
        selected_plan = current_user.plan_set.filter(id=plan_id).first()
        # Return the plan information.
        return Response(
            {
                'error': 0,
                'message': 'Success',
                'data': {
                    'shifts_per_day': selected_plan.plan_schedule.total_shifts_per_day,
                    'schedule': selected_plan.plan_schedule.last_solutions["0"],
                    'tasks': dict([
                        (
                            task.name,
                            {
                                'name': task.name,
                                'display': task.display_name,
                                'description': task.task_description
                            }
                        ) for task in selected_plan.plan_schedule.tasks.all()
                    ]),
                    'meals': PlanOperations.get_plan_meals_schedule(selected_plan)
                }
            },
            status=200,
            content_type='application/json'
        )
