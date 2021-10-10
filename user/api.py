from rest_framework import serializers
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from user.models import User, Profile, Country
from user.serializers import UserProfileUpdateSerializer, \
    DoneeAndNgoProfileCreateUpdateSerializer, CountrySerializer, CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    # Replace the serializer with your custom
    serializer_class = CustomTokenObtainPairSerializer


class UserUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = UserProfileUpdateSerializer

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        user = User.objects.filter(username=request.data["username"]).exclude(id=request.user.id)
        if user:
            raise serializers.ValidationError('Username must be unique.')
        return self.update(request, *args, **kwargs)


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