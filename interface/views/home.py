from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView


# The page for displaying the home page.
class HomePage(APIView):
    # The class used for rendering.
    renderer_classes = [TemplateHTMLRenderer]

    # The GET method for this class.
    def get(self, request):
        # Check if user is not authenticated.
        if not request.user.is_authenticated:
            # Map the context.
            context = {}
            # Return the non logged in page.
            return Response(
                context,
                template_name='demos/main/home/home_page_no_auth.html'
            )
        # Map the context.
        context = {}
        # Return the response with the html content.
        return Response(
            context,
            template_name='demos/main/home/home_page_auth.html'
        )
