from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView


# The page for displaying the registration page.
class LogoutPage(LoginRequiredMixin, APIView):
    # The class used for rendering.
    renderer_classes = [TemplateHTMLRenderer]
    # The login url.
    login_url = '/login'

    # The POST method for this class.
    def post(self, request):
        # Logout the user.
        logout(request)
        # Redirect to home.
        return redirect('/')
