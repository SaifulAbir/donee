from rest_framework.generics import  CreateAPIView
from .serializers import *



class PaymentCreateAPIView(CreateAPIView):
    serializer_class = PaymentSerializer
