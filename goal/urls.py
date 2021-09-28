from django.urls import path
from .views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('page/', csrf_exempt(DoneeAndNgoProfileView.as_view())),
    
    ]

