from django.urls import path
from .api import *

urlpatterns = [
    path('live-notification-list/', LiveNotificationListAPI.as_view()),
]