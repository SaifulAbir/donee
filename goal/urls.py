from django.urls import path
from .api import *

urlpatterns = [
    path('sdgs-list/', SDGSListAPI.as_view()),
]

