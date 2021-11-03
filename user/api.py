from django.db.models import Count, Q
from django.db.models.functions import Concat
from django.db.models.query import Prefetch
from rest_framework import serializers
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from payment.models import Payment
from user.models import User, Profile, Country,Notification,ProfileFollow,UserFollow
from user.serializers import UserProfileUpdateSerializer, \
    DoneeAndNgoProfileCreateUpdateSerializer, CountrySerializer, CustomTokenObtainPairSerializer, DonorProfileSerializer,UserFollowUserSerializer,UserFollowProfileSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError



class CustomTokenObtainPairView(TokenObtainPairView):
    # Replace the serializer with your custom
    serializer_class = CustomTokenObtainPairSerializer


class UserUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = UserProfileUpdateSerializer

    def get_object(self):
        user = User.objects.filter(id=self.request.user.id).prefetch_related(
            Prefetch('user_notification',queryset = Notification.objects.filter(profile__isnull=True))).prefetch_related(
            Prefetch("user_payment", queryset=Payment.objects.filter(status="PAID").distinct('goal'))).annotate(
            total_supported_goals=Count(
                Concat('user_payment__user', 'user_payment__goal'),
                filter=Q(user_payment__status='PAID'),
                distinct=True
            )
        )
        return user.first()

    def put(self, request, *args, **kwargs):
        try:
            user = User.objects.filter(username=request.data["username"]).exclude(id=request.user.id)
            if user:
                raise serializers.ValidationError('Username must be unique.')
            return self.update(request, *args, **kwargs)
        except KeyError:
            return self.update(request, *args, **kwargs)


class DonorProfileAPIView(RetrieveAPIView):
    serializer_class = DonorProfileSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny, ]


class DoneeAndNgoProfileCreateAPIView(CreateAPIView):
    serializer_class = DoneeAndNgoProfileCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return super(DoneeAndNgoProfileCreateAPIView, self).post(request, *args, **kwargs)


class DoneeAndNgoProfileUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = DoneeAndNgoProfileCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class CountryListAPI(ListAPIView):
    queryset = Country.objects.filter()
    serializer_class = CountrySerializer



class UserFollowUserAPI(CreateAPIView):
    serializer_class = UserFollowUserSerializer
    queryset = UserFollow.objects.all()

    def create(self, request, *args, **kwargs):
        if self.request.data =={} :
            raise ValidationError({"follow_user":'this field is required'})
        else:
            if isinstance(self.request.data['follow_user'], int):
                user = User.objects.get(id = self.request.user.id)
                follow_user = User.objects.get(id = self.request.data['follow_user'])
                check_follow = UserFollow.objects.filter(user = self.request.user.id,follow_user = self.request.data['follow_user']) #check follower user
                check_profile = Profile.objects.filter(user = self.request.user.id)
                if check_follow.exists() and check_follow.first().is_follow == True:
                    obj = check_follow.first()
                    obj.is_follow = False
                    obj.save()
                    follow_user_obj = follow_user
                    follow_user.total_follow_count -=1
                    follow_user_obj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"follow_user":self.request.data["follow_user"],"is_follow":False,}, status=status.HTTP_200_OK)
                if check_follow.exists() and check_follow.first().is_follow == False:
                    obj = check_follow.first()
                    obj.is_follow = True
                    obj.save()
                    follow_user_obj = follow_user
                    follow_user_obj.total_follow_count +=1
                    follow_user_obj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"follow_user":self.request.data["follow_user"],"is_follow":True,}, status=status.HTTP_200_OK)
                
                if check_profile.exists():
                      raise ValidationError({"follow_user":'profile id is not allowed'})  
                else:
                    follow_user_obj = follow_user
                    follow_user_obj.total_follow_count +=1
                    follow_user_obj.save()
                    followobj= UserFollow(user = user,follow_user = follow_user,is_follow = True,created_by =user.username)
                    followobj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"follow_user":self.request.data["follow_user"],"is_follow":True,}, status=status.HTTP_201_CREATED)
            else:
                raise ValidationError({"follow_user":'must provide integer user id!'})



class UserFollowProfileAPI(CreateAPIView):
    serializer_class = UserFollowProfileSerializer
    queryset = ProfileFollow.objects.all()

    def create(self, request, *args, **kwargs):
        if self.request.data =={} :
            raise ValidationError({"follow_profile":'this field is required'})
        else:
            if isinstance(self.request.data['follow_profile'], int):
                user = User.objects.get(id = self.request.user.id)
                follow_profile = Profile.objects.get(id = self.request.data['follow_profile'])
                check_follow = ProfileFollow.objects.filter(user = self.request.user.id,follow_profile = self.request.data['follow_profile'])  #check follower user
                check_profile = Profile.objects.filter(user = self.request.user.id)
                if check_follow.exists() and check_follow.first().is_follow == True:
                    obj = check_follow.first()
                    obj.is_follow = False
                    obj.save()
                    follow_profile_obj = follow_profile
                    follow_profile.total_follow_count -=1
                    follow_profile_obj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"follow_profile":self.request.data["follow_profile"],"is_follow":False,}, status=status.HTTP_200_OK)
                if check_follow.exists() and check_follow.first().is_follow == False:
                    obj = check_follow.first()
                    obj.is_follow = True
                    obj.save()
                    follow_profile_obj = follow_profile
                    follow_profile_obj.total_follow_count +=1
                    follow_profile_obj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"follow_profile":self.request.data["follow_profile"],"is_follow":True,}, status=status.HTTP_200_OK)
                
                if check_profile.exists():
                      raise ValidationError({"follow_profile":'profile id is not allowed'})  
                else:
                    follow_profile_obj = follow_profile
                    follow_profile_obj.total_follow_count +=1
                    follow_profile_obj.save()
                    followobj= ProfileFollow(user = user,follow_profile = follow_profile,is_follow = True,created_by =user.username)
                    followobj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"follow_profile":self.request.data["follow_profile"],"is_follow":True,}, status=status.HTTP_201_CREATED)
            else:
                raise ValidationError({"follow_profile":'must provide integer user id!'})