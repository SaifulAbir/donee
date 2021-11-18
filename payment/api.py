from rest_framework.generics import  CreateAPIView
from .serializers import *


class PaymentCreateAPIView(CreateAPIView):
    serializer_class = PaymentSerializer


class TransactionCreateAPIView(CreateAPIView):
    serializer_class = TransactionSerializer


class CashoutCreateAPIView(CreateAPIView):
    serializer_class = CashoutSerializer
