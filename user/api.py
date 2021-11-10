from django.db.models import Count, Q, F
from django.db.models.functions import Concat
from django.db.models.query import Prefetch, QuerySet
from rest_framework import serializers
from rest_framework import response
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from payment.models import Payment
from user.models import User, Profile, Country,Notification,ProfileFollow,UserFollow
from goal.models import Goal, GoalSave
from user.serializers import UserProfileUpdateSerializer, \
    DoneeAndNgoProfileCreateUpdateSerializer, CountrySerializer, CustomTokenObtainPairSerializer, \
    DonorProfileSerializer, DoneeAndNGOProfileSerializer, UserFollowUserSerializer, UserFollowProfileSerializer, \
        InNgoDoneeInfoSerializer, InNgoDoneeListSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from user.utils import profile_view_count


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
        ).prefetch_related(
            Prefetch('goalsave_user', queryset=GoalSave.objects.filter(is_saved=True).distinct('goal')))
        return user.first()

    def put(self, request, *args, **kwargs):
        try:
            user = User.objects.filter(username=request.data["username"]).exclude(id=request.user.id)
            if user:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
            return self.update(request, *args, **kwargs)
        except KeyError:
            return self.update(request, *args, **kwargs)


class DonorProfileAPIView(RetrieveAPIView):
    serializer_class = DonorProfileSerializer
    permission_classes = [AllowAny, ]

    def get_object(self):
        user_id = self.kwargs['pk']
        user = User.objects.annotate(
            total_supported_goals=Count(
                Concat('user_payment__user', 'user_payment__goal'),
                filter=Q(user_payment__status='PAID'),
                distinct=True
            )
        ).prefetch_related(
            Prefetch("user_payment", queryset=Payment.objects.filter(status="PAID").distinct('goal'))).get(id=user_id)
        return user


class DoneeAndNGOProfileAPIView(RetrieveAPIView):
    serializer_class = DoneeAndNGOProfileSerializer
    permission_classes = [AllowAny, ]

    def get_object(self):
        profile_id = self.kwargs['pk']
        queryset = Profile.objects.annotate(
            total_donor=Count(
                Concat('profile_goal__goal_payment__goal', 'profile_goal__goal_payment__user'),
                filter=Q(profile_goal__goal_payment__status='PAID'),
                distinct=True
            ),
            total_completed_goals = Count(
                'profile_goal', filter=Q(profile_goal__paid_amount=F('profile_goal__total_amount'))
            )
        ).get(id=profile_id)
        profile_view_count(queryset)
        return queryset


class DoneeAndNgoProfileCreateAPIView(CreateAPIView):
    serializer_class = DoneeAndNgoProfileCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return super(DoneeAndNgoProfileCreateAPIView, self).post(request, *args, **kwargs)


class DoneeAndNgoProfileUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = DoneeAndNgoProfileCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Profile.objects.annotate(
            total_donor=Count(
                Concat('profile_goal__goal_payment__goal', 'profile_goal__goal_payment__user'),
                filter=Q(profile_goal__goal_payment__status='PAID'),
                distinct=True
            ),
            total_completed_goals = Count(
                'profile_goal', filter=Q(profile_goal__paid_amount=F('profile_goal__total_amount'))
            )
        ).get(user=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class inNgoDoneeInfoAPIView(RetrieveAPIView):
    serializer_class = InNgoDoneeInfoSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Profile.objects.get(user=self.request.user)


class inNgoDoneeListAPIView(ListAPIView):
    serializer_class = InNgoDoneeListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        ngo_obj= Profile.objects.get(user=self.request.user)
        return Profile.objects.filter(ngo_profile_id=ngo_obj.id)

       


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
                if check_follow.exists() and check_follow.first().is_followed == True:
                    obj = check_follow.first()
                    obj.is_followed = False
                    obj.save()
                    follow_user_obj = follow_user
                    user_obj = user
                    follow_user.total_follow_count -=1
                    user.total_following_count -=1
                    print(user.total_following_count)
                    follow_user_obj.save()
                    user_obj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"follow_user":self.request.data["follow_user"],"is_followed":False,}, status=status.HTTP_200_OK)
                if check_follow.exists() and check_follow.first().is_followed == False:
                    obj = check_follow.first()
                    obj.is_followed = True
                    obj.save()
                    follow_user_obj = follow_user
                    user_obj = user
                    follow_user_obj.total_follow_count +=1
                    user_obj.total_following_count +=1
                    print(user.total_following_count)
                    follow_user_obj.save()
                    user_obj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"follow_user":self.request.data["follow_user"],"is_followed":True,}, status=status.HTTP_200_OK)

                
                else:
                    follow_user_obj = follow_user
                    user_obj = user
                    follow_user_obj.total_follow_count +=1
                    user_obj.total_following_count +=1
                    print(user.total_following_count)
                    follow_user_obj.save()
                    user_obj.save()
                    followobj= UserFollow(user = user,follow_user = follow_user,is_followed = True,created_by =user.username)
                    followobj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"follow_user":self.request.data["follow_user"],"is_followed":True,}, status=status.HTTP_201_CREATED)
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
                if check_follow.exists() and check_follow.first().is_followed == True:
                    obj = check_follow.first()
                    obj.is_followed = False
                    obj.save()
                    follow_profile_obj = follow_profile
                    user_obj = user
                    follow_profile.total_follow_count -=1
                    user_obj.total_following_count -=1
                    print(user.total_following_count)
                    follow_profile_obj.save()
                    user_obj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"follow_profile":self.request.data["follow_profile"],"is_followed":False,}, status=status.HTTP_200_OK)
                if check_follow.exists() and check_follow.first().is_followed == False:
                    obj = check_follow.first()
                    obj.is_followed = True
                    obj.save()
                    follow_profile_obj = follow_profile
                    user_obj = user
                    follow_profile_obj.total_follow_count +=1
                    user_obj.total_following_count +=1
                    print(user.total_following_count)
                    follow_profile_obj.save()
                    user_obj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"follow_profile":self.request.data["follow_profile"],"is_followed":True,}, status=status.HTTP_200_OK)

            
                else:
                    follow_profile_obj = follow_profile
                    user_obj = user
                    follow_profile_obj.total_follow_count +=1
                    user_obj.total_following_count +=1
                    print(user.total_following_count)
                    follow_profile_obj.save()
                    user_obj.save()
                    followobj= ProfileFollow(user = user,follow_profile = follow_profile,is_followed = True,created_by =user.username)
                    followobj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"follow_profile":self.request.data["follow_profile"],"is_followed":True,}, status=status.HTTP_201_CREATED)
            else:
                raise ValidationError({"follow_profile":'must provide integer user id!'})