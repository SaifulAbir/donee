from django.db.models import Count, Q, F
from django.db.models.functions import Concat
from django.db.models.query import Prefetch
from rest_framework import serializers
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from payment.models import Payment
from user.models import User, Profile, Country,Notification
from user.serializers import UserProfileUpdateSerializer, \
    DoneeAndNgoProfileCreateUpdateSerializer, CountrySerializer, CustomTokenObtainPairSerializer, \
    DonorProfileSerializer, DoneeAndNGOProfileSerializer


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


class DoneeAndNGOProfileAPIView(RetrieveAPIView):
    serializer_class = DoneeAndNGOProfileSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        queryset = Profile.objects.annotate(
            total_donor=Count(
                Concat('profile_goal__goal_payment__goal', 'profile_goal__goal_payment__user'),
                filter=Q(profile_goal__goal_payment__status='PAID'),
                distinct=True
            ),
            total_completed_goals = Count(
                'profile_goal', filter=Q(profile_goal__paid_amount=F('profile_goal__total_amount'))
            )
        )
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
        return Profile.objects.get(user=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class CountryListAPI(ListAPIView):
    queryset = Country.objects.filter()
    serializer_class = CountrySerializer