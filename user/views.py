from rest_framework import status
from .serializers import *
from rest_framework.generics import CreateAPIView, ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, \
    RetrieveAPIView, UpdateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError




class UserRegApi(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegSerializer
    permission_classes = [AllowAny]

        



class DoneeAndNgoProfileView(ListCreateAPIView):

    serializer_class = DoneeAndNgoProfileSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self) :
        # print(Profile.objects.filter(user__email=self.request.user).query)
        return Profile.objects.filter(user__email=self.request.user)
       

    # have to handle post method here