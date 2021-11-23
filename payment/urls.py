from django.urls import path
from .api import *


urlpatterns = [
    path('create/payment/', PaymentCreateAPIView.as_view()),
    path('create/transaction/', TransactionCreateAPIView.as_view()),
    path('create/cashout/', CashoutCreateAPIView.as_view()),
    path('cashout-history-list/', CashoutHistoryListAPIView.as_view()),
    path('waiting-for-admin-list/', WaitingforAdminListAPIView.as_view()),
    path('waiting-for-ngo-list/', WaitingforNGOListAPIView.as_view()),

]

