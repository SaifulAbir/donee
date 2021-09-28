from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(User)
admin.site.register(ProfileType)
admin.site.register(Plan)
admin.site.register(Profile)