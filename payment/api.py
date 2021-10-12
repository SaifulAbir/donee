from rest_framework.generics import  CreateAPIView
from .serializers import *



class TransactionCreateAPIView(CreateAPIView):
    serializer_class = TransactionSerializer
