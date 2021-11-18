from django.urls import path
from .api import *


urlpatterns = [
    path('create/payment/', PaymentCreateAPIView.as_view()),
    path('create/transaction/', TransactionCreateAPIView.as_view()),
    path('create/cashout/', CashoutCreateAPIView.as_view()),

]

