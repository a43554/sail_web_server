from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from rest_framework.views import APIView

# The page for plan copying.
from main.models import Plan, PlanAccess


class PlanGenerator(LoginRequiredMixin, APIView):
    # The login url.
    login_url = '/login'

    # The POST method for this class.
    def post(self, request):
        # Add each item to the access.
        with transaction.atomic():
            # Create a copy of the plan.
            new_plan = Plan(
                name="Novo Plano",
                description="Nenhuma descrição disponível"
            )
            # Save the plan.
            new_plan.save()
            # Add this user to the assigned users.
            PlanAccess(
                plan=new_plan,
                user=request.user,
                level=PlanAccess.OWNER
            ).save()
        # Redirect to home.
        return redirect(f'/plans/{new_plan.id}')
