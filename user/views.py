from rest_framework import status
from .serializers import *
from rest_framework import views
from rest_framework.generics import CreateAPIView, ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, \
    RetrieveAPIView, UpdateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User,Profile
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError




class UserRegApi(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegSerializer
    permission_classes = [AllowAny]




class VerifyInvitationView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        invitation = self.kwargs['invitation']
        check_id = Profile.objects.filter(invitation_id=invitation)
        for i in check_id:
            ngo_id = i.id
        if check_id.exists():
            return Response({'ngo_profile_id':ngo_id})
        else:
            return Response({'error':'400 invitation not code found.'})
        
        

    # def post(self, request,*args, **kwargs):
    #     check_id = Profile.objects.filter(invitation_id=self.request.data['check_id'])
       
    #     if check_id.exists():
    #         return Response({'success':'200 invitation code found.'})
    #     else:
    #         return Response({'error':'400 invitation not code found.'})