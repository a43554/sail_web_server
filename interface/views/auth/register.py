from django.shortcuts import redirect
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from django.contrib.auth import get_user_model

# The page for displaying the registration page.
class RegisterPage(APIView):
    # The class used for rendering.
    renderer_classes = [TemplateHTMLRenderer]

    class RegisterSerializer(serializers.Serializer):
        username = serializers.CharField(
            max_length=100,
            label='Nome',
            style={
                'placeholder': 'Nome de usuario',
                'autofocus': True,
                'template': 'demos/main/auth/signup_field.html'
            }
        )
        password = serializers.CharField(
            max_length=100,
            label='Palavra-Passe',
            style={
                'input_type': 'password',
                'placeholder': 'Palavra-Passe',
                'template': 'demos/main/auth/signup_field.html'
            }
        )
        confirm_password = serializers.CharField(
            max_length=100,
            label='Confirmar Palavra-Passe',
            style={
                'input_type': 'password',
                'placeholder': 'Palavra-Passe',
                'template': 'demos/main/auth/signup_field.html'
            },
        )

        # Validate the form.
        def validate(self, data):
            # Check if any of the fields are empty.
            if not data.get('password') or not data.get('confirm_password'):
                # Raise an exception.
                raise serializers.ValidationError("Please enter a password and confirm it.")
            # Check if passwords do not match.
            if data.get('password') != data.get('confirm_password'):
                # Raise an exception.
                raise serializers.ValidationError("Passwords do not match.")
            # Return the data.
            return data

    # The GET method for this class.
    def get(self, request):
        # Return the response with the html content.
        return Response(
            {'serializer': RegisterPage.RegisterSerializer()},
            template_name='demos/main/auth/signup_page.html'
        )

    # The POST method for this class.
    def post(self, request):
        # Obtain the serializable.
        serializer = RegisterPage.RegisterSerializer(data=request.data)
        # Check if result is not valid.
        if not serializer.is_valid():
            # Return the response with the html content.
            return Response(
                {'serializer': serializer},
                template_name='demos/main/auth/signup_page.html'
            )
        # Create a new user.
        User = get_user_model()
        # Create a user, if none exists.
        User.objects.create_user(username=request.data.get('username'), password=request.data.get('password'))
        # Redirect to home.
        return redirect('/login')
