from rest_framework.response import Response
from rest_framework.views import APIView

from system.models import Client
from utils.auth.bearer import BearerAuthentication


# The login application view.
class MobilePlanView(APIView):
    # The authentication classes.
    authentication_classes = [BearerAuthentication]

    # The "GET" method for this view.
    def get(self, request):
        # Obtain the user.
        current_user: Client = request.user
        # Obtain the user's finished plans.
        completed_plans = current_user.plan_set.filter(plan_completion=True)
        # Return the plans.
        return Response(
            {
                'error': 0,
                'message': 'Success',
                'data': [{
                    'id': plan.id,
                    'title': plan.name,
                    'description': plan.description,
                } for plan in completed_plans]
            },
            status=200,
            content_type='application/json; charset=utf-8'
        )