from django.urls import path, re_path
from rest_framework.authtoken import views
from ..views import *

urlpatterns = [
    # The api paths.
    path('plans/new/', PlanGenerator.as_view()),
    path('plans/<str:plan_id>/copy', PlanCopier.as_view()),
    path('api/plans/<str:plan_id>/edit', PlanMakerEdit.as_view()),
    path('api/plans/<str:plan_id>/', PlanMaker.as_view()),
    path('api/plans/<str:plan_id>/task-switch', PlanMakerSwitchTask.as_view()),

    # Mobile API paths.
    path('mobile-api/login/', views.obtain_auth_token),
    path('mobile-api/plans/', MobilePlanView.as_view()),
    path('mobile-api/plans/<int:plan_id>/', MobilePlanInformationView.as_view()),

    # UI auth paths.
    path('logout/', LogoutPage.as_view()),
    path('register/', RegisterPage.as_view()),
    path('login/', LoginPage.as_view()),

    # UI paths.
    path('', HomePage.as_view()),
    path('plans/', PlanListPage.as_view()),
    path('plans/<int:plan_id>/', PlanStartPage.as_view()),

    # re_path(r"^info/(?P<_id>\w+)/$", WineInfo.as_view()),
    # re_path(r"^info/(?P<language>[a-zA-Z]{2})/(?P<_id>\w+)/$", WineInfo.as_view()),
    # path('<str:_id>/', WinePage.as_view()),
    # re_path(r'^(?P<language>[a-zA-Z]{2})/(?P<_id>\w+)/$', WinePage.as_view()),
]