from rest_framework import serializers
from notification.models import LiveNotification
from user.serializers import UserSerializer


class LiveNotificationSerializer(serializers.ModelSerializer):
    from_user = UserSerializer()
    class Meta:
        model = LiveNotification
        fields = ['id', 'text', 'type', 'from_user', 'to_user', 'created_at']

class LiveNotificationUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = LiveNotification
        fields = ['id', 'is_read']
        

