from django.urls import path
from .api import *

urlpatterns = [
    path('live-notification-list/', LiveNotificationListAPI.as_view()),
    path('live-notification-read-update/<int:pk>/', LiveNotificationUpdateAPI.as_view()),

]