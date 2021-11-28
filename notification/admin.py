from django.contrib import admin

# Register your models here.
from Donee.admin import DoneeAdmin
from notification.models import LiveNotification

admin.site.register(LiveNotification, DoneeAdmin)
