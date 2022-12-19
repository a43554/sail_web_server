from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.shortcuts import redirect
from rest_framework.exceptions import ErrorDetail
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from django.contrib.auth import authenticate, login


# The page for displaying the registration page.
from system.models import Client


class LoginPage(APIView):
    # The class used for rendering.
    renderer_classes = [TemplateHTMLRenderer]

    class LoginSerializer(serializers.Serializer):
        username = serializers.CharField(
            max_length=100,
            label='Utilizador',
            error_messages={
                'required': 'Este campo não pode ser deixado em branco',
                'invalid': 'Utilizador não encontrado',
            },
            style={
                'placeholder': 'Nome de usuario',
                'template': 'demos/main/auth/signup_field.html',
                'autofocus': True,
            }
        )
        password = serializers.CharField(
            max_length=100,
            label='Palavra-Passe',
            error_messages={
                'required': 'Este campo não pode ser deixado em branco',
                'invalid': 'Palavra-passe incorreta',
            },
            style={
                'placeholder': 'Palavra-Passe',
                'template': 'demos/main/auth/signup_field.html',
                'input_type': 'password',
            }
        )
        remember_me = serializers.BooleanField(
            label='Manter sessão iniciada',
            style={
                'template': 'demos/main/auth/check_field.html',
            }
        )

    # The GET method for this class.
    @method_decorator(never_cache)
    def get(self, request):
        # Check if user is authenticated.
        if request.user.is_authenticated:
            # Redirect to home.
            return redirect('/')
        # Return the response with the html content.
        return Response(
            {'serializer': LoginPage.LoginSerializer()},
            template_name='demos/main/auth/signin_page.html'
        )

    # The POST method for this class.
    def post(self, request):
        # Obtain the serializable.
        serializer = LoginPage.LoginSerializer(data=request.data)
        # Check if result is not valid.
        if not serializer.is_valid():
            # Return the response with the html content.
            return Response(
                {'serializer': serializer},
                template_name='demos/main/auth/signin_page.html'
            )
        # The input username.
        input_username = request.data.get('username')
        # Check if the username exists.
        if Client.objects.filter(username=input_username).count() == 0:
            # Set an error.
            serializer._errors["username"] = [ErrorDetail(string="Utilizador não encontrado", code="invalid")]
            # Username does not exist.
            return Response(
                {'serializer': serializer},
                template_name='demos/main/auth/signin_page.html'
            )
        # Authenticate the user.
        user = authenticate(request, username=input_username, password=request.data.get('password'))
        # Check if the user is not authenticated.
        if user is None:
            # Set an error.
            serializer._errors["password"] = [ErrorDetail(string="Palavra-passe incorreta.", code="invalid")]
            # Return an error.
            return Response(
                {'serializer': serializer},
                template_name='demos/main/auth/signin_page.html'
            )
        # Otherwise.
        else:
            # Login the user.
            login(request, user)
            # Check if remember me is turned on.
            if not request.data.get('remember_me'):
                # Set the session to not expire.
                request.session.set_expiry(0)
            # Redirect to home.
            return redirect('/')
