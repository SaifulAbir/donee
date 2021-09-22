from django.urls import path
from .views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('reguserapi/', csrf_exempt(UserRegApi.as_view())),
    path('userprofileupdate/', csrf_exempt(UserProfileUpdateView.as_view())),
    path('profilecreate/', csrf_exempt(DoneeAndNgoProfileView.as_view())),
    ]

