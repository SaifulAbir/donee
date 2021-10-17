from django.urls import path
from .api import *


urlpatterns = [
    path('donate/', PaymentCreateAPIView.as_view()),
  
]

