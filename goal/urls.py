from django.urls import path
from .api import *
from .views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('page/', csrf_exempt(DoneeAndNgoProfileView.as_view())),
    path('sdgs-list/', SDGSListAPI.as_view()),
]

