from rest_framework import serializers
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from user.models import User, Profile
from user.serializers import UserProfileUpdateSerializer, \
    DoneeAndNgoProfileCreateUpdateSerializer


class UserUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        user = User.objects.filter(username=request.data["username"])
        if user:
            raise serializers.ValidationError('Username must be unique.')
        return self.update(request, *args, **kwargs)


class DoneeAndNgoProfileCreateAPIView(CreateAPIView):
    serializer_class = DoneeAndNgoProfileCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.filter(profile_name=request.data["profile_name"])
        except KeyError:
            profile = None
        if profile:
            raise serializers.ValidationError('Profile name must be unique.')
        return super(DoneeAndNgoProfileCreateAPIView, self).post(request, *args, **kwargs)


class DoneeAndNgoProfileUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = DoneeAndNgoProfileCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

    def put(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.filter(profile_name=request.data["profile_name"])
        except KeyError:
            profile = None
        if profile:
            raise serializers.ValidationError('Profile name must be unique.')
        return self.update(request, *args, **kwargs)