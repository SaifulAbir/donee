from django.urls import path
from .api import *
from .views import *

urlpatterns = [
    path('sdgs-list/', SDGSListAPI.as_view()),
    path('create-goal/', GoalCreateAPIView.as_view()),
    path('goal-list/', GoalListAPI.as_view()),
    path('single-catagory/<str:title>', SingleCatagoryView.as_view()),
    path('retrieve-goal/<str:slug>/', GoalRetrieveUpdateAPIView.as_view()),
]

