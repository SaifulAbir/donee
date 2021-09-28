from rest_framework import status
from .serializers import *
from rest_framework.generics import CreateAPIView, ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, \
    RetrieveAPIView,UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError




class UserRegApi(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegSerializer
    permission_classes = [AllowAny]



class UserProfileUpdateView(ListCreateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) :
        # user = self.request.user
        return User.objects.filter(email=self.request.user)


  
    def post(self, request, *args, **kwargs):
        
        # queryset = User.objects.filter(username = self.request.data['username'])
        # if queryset.exists():
        #     raise ValidationError('Username already taken')

       

        user = User.objects.get(email=self.request.user)

        if request.data.get('image'):
            user.username = request.data.get('username') or user.username
            user.full_name = request.data.get('full_name') or user.full_name
            user.location = request.data.get('location') or user.location
            user.phone_number = request.data.get('phone_number') or  user.phone_number
            user.bio = request.data.get('bio') or  user.bio
            user.image = self.request.FILES(['image']) 
            user.save()
            return Response({'Success':'User Profile Created'}, status=status.HTTP_201_CREATED)
        else :
            user.username = request.data.get('username') or user.username
            user.full_name = request.data.get('full_name') or user.full_name
            user.location = request.data.get('location') or user.location
            user.phone_number = request.data.get('phone_number') or  user.phone_number
            user.bio = request.data.get('bio') or  user.bio
            user.save()
            return Response({'Success':'User Profile Created'}, status=status.HTTP_201_CREATED)

        



class DoneeAndNgoProfileView(ListCreateAPIView):

    serializer_class = DoneeAndNgoProfileSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self) :
        # print(Profile.objects.filter(user__email=self.request.user).query)
        return Profile.objects.filter(user__email=self.request.user)
       

    # have to handle post method here