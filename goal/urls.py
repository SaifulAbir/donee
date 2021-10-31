from django.urls import path
from .api import *

urlpatterns = [
    path('sdgs-list/', SDGSListAPI.as_view()),
    path('create-goal/', GoalCreateAPIView.as_view()),
    path('goal-list/', GoalListAPI.as_view()),
    path('popular-goals/', PopularGoalAPI.as_view()),
    path('supported-goals/', SupportedGoalAPI.as_view()),
    path('search/', SearchAPIView.as_view()),
    path('single-catagory/<int:id>', SingleCatagoryView.as_view()),
    path('retrieve-goal/<str:slug>/', GoalRetrieveUpdateAPIView.as_view()),
    path('goal-like/', GoalLikeAPI.as_view()),
    path('goal-comment/', GoalCommentAPI.as_view()),
    path('goal-save/', GoalSaveAPI.as_view()),
]

