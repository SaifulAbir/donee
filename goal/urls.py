from django.urls import path
from .api import *

urlpatterns = [
    path('sdgs-list/', SDGSListAPI.as_view()),
    path('create-goal/', GoalCreateAPIView.as_view()),
]

