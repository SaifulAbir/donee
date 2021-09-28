from django.urls import path
from .views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('create-user/', csrf_exempt(UserRegApi.as_view())),
    path('update-user/', csrf_exempt(UserProfileUpdateView.as_view())),
    path('profile-create/', csrf_exempt(DoneeAndNgoProfileView.as_view())),
    ]

