import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from Donee.models import DoneeModel
from user.models import User


class LiveNotification(DoneeModel):
    NOTIFICATION_TYPES = [
        ('DONEE_GOAL_CREATION', 'Donee Goal Creation'),
    ]

    text = models.CharField(max_length=500)
    type = models.CharField(max_length=100, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    from_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="from_user_notification")
    to_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="to_user_notification")

    class Meta:
        verbose_name = 'Live Notification'
        verbose_name_plural = 'Live Notifications'
        db_table = 'live_notifications'

    def __str__(self):
        return self.text

# @receiver(post_save, sender=LiveNotification)
# def notification_post_save(sender, instance, *args, **kwargs):
#     from notification.serializers import LiveNotificationSerializer
#     channel_layer = get_channel_layer()
#
#     group_name = "notifications"
#     async_to_sync(channel_layer.group_send)(
#         group_name,
#         {
#             'type': 'notify',
#             'text': LiveNotificationSerializer(instance, many=False).data
#             # 'text': "jkdfkdsljfldslkdfj"
#         }
#     )
