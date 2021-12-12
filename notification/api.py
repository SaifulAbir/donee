from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.views import APIView
from notification.models import LiveNotification
from notification.serializers import LiveNotificationSerializer, LiveNotificationUpdateSerializer


class LiveNotificationListAPI(ListAPIView):
    serializer_class = LiveNotificationSerializer

    def get_queryset(self):
        return LiveNotification.objects.filter(to_user=self.request.user).order_by('-created_at')

class LiveNotificationUpdateAPI(UpdateAPIView):
    queryset=LiveNotification.objects.all()
    serializer_class=LiveNotificationUpdateSerializer
