from rest_framework import serializers
from notification.models import LiveNotification


class LiveNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = LiveNotification
        fields = ['id', 'text', 'type', 'from_user', 'to_user']