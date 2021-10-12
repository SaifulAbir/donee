from django.urls import path
from .api import *


urlpatterns = [
    path('donate/', TransactionCreateAPIView.as_view()),
  
]

