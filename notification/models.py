import json
import requests
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from Donee.models import DoneeModel
from user.models import User


class LiveNotification(DoneeModel):
    NOTIFICATION_TYPES = [
        ('DONEE_GOAL_CREATION', 'Donee Goal Creation'),
        ('DONEE_INVITATION_ACCEPT', 'Donee Invitation Accept'),
        ('DONEE_GOAL_APPROVE', 'Donee Goal Approve'),
        ('DONATION', 'Donation'),
        ('GOAL_LIKE', 'Goal Like'),
        ('GOAL_COMMENT', 'Goal Comment'),
        ('PROFILE_FOLLOW', 'Profile Follow'),
        ('DONEE_CASHOUT_REQUEST', 'Donee Cashout Request'),
        ('NGO_CASHOUT_REQUEST', 'NGO Cashout Request'),
        ('DONEE_CASHOUT_ACCEPT', 'Donee Cashout Accept'),
        ('DONEE_CASHOUT_REJECT', 'Donee Cashout Reject'),
        ('NGO_CASHOUT_ACCEPT', 'Donee Cashout Accept'),
        ('NGO_CASHOUT_REJECT', 'Donee Cashout Reject'),
    ]
    text = models.CharField(max_length=500)
    type = models.CharField(max_length=100, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    identifier = models.CharField(max_length=255)
    from_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="from_user_notification")
    to_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="to_user_notification")

    class Meta:
        verbose_name = 'Live Notification'
        verbose_name_plural = 'Live Notifications'
        db_table = 'live_notifications'

    def __str__(self):
        return self.text


@receiver(post_save, sender=LiveNotification)
def notification_post_save(sender, instance, *args, **kwargs):
    from notification.serializers import LiveNotificationSerializer
    url = "https://socket.doneeapp.com/api/send-notification/"
    payload = {"notification": json.dumps(LiveNotificationSerializer(instance, many=False).data)}
    requests.post(url, data=payload)
