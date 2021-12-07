from rest_framework.generics import ListAPIView
from notification.models import LiveNotification
from notification.serializers import LiveNotificationSerializer


class LiveNotificationListAPI(ListAPIView):
    serializer_class = LiveNotificationSerializer

    def get_queryset(self):
        return LiveNotification.objects.filter(to_user=self.request.user)