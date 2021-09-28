from rest_framework import serializers
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from user.models import User
from user.serializers import UserProfileUpdateSerializer


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