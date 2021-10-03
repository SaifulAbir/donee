from django.urls import path
from .api import UserUpdateAPIView, DoneeAndNgoProfileCreateAPIView, DoneeAndNgoProfileUpdateAPIView, CountryListAPI
from .views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('create-user/', csrf_exempt(UserRegApi.as_view())),
    path('update-user/', UserUpdateAPIView.as_view()),
    path('create-profile/', DoneeAndNgoProfileCreateAPIView.as_view()),
    path('update-profile/', DoneeAndNgoProfileUpdateAPIView.as_view()),
    path('country-list/', CountryListAPI.as_view()),
]

