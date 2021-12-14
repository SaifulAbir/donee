from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from notification.models import LiveNotification
from notification.serializers import LiveNotificationUpdateSerializer, LiveNotificationSerializer


class LiveNotificationListAPI(APIView):
    serializer_class = LiveNotificationSerializer

    def get(self, *args):
        query =LiveNotification.objects.filter(to_user=self.request.user).order_by('-created_at')
        unread_count = 0
        read_count = 0
        for read_obj in query:
            if read_obj.is_read:
                read_count+=1
            else:
                unread_count+=1

        serializer = LiveNotificationSerializer(query, many=True)

        return Response({'read_count':read_count, 'unread_count':unread_count, 'list':serializer.data})

class LiveNotificationUpdateAPI(UpdateAPIView):
    queryset=LiveNotification.objects.all()
    serializer_class=LiveNotificationUpdateSerializer
