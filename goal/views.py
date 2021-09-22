from rest_framework import status
from .serializers import *
from rest_framework.generics import CreateAPIView, ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, \
    RetrieveAPIView,UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import *
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError





class DoneeAndNgoProfileView(ListCreateAPIView):

    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self) :
        # print(Profile.objects.filter(user__email=self.request.user).query)
        return Goal.objects.filter(profile_id__user__email=self.request.user)

 
    def perform_create(self, serializer):
            user = Profile.objects.get(user__email=self.request.user)
            serializer.save(profile_id=user,pgw_amount=10,ngo_amount=10,platform_amount=10,total_amount=100,status='Draft')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
