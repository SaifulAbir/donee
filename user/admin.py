from django.contrib import admin


from Donee.admin import DoneeAdmin
from .models import *
# Register your models here.


admin.site.register(User)
admin.site.register(Plan)
admin.site.register(Profile)
admin.site.register(Country)
admin.site.register(UserFollow)
admin.site.register(ProfileFollow)
admin.site.register(NgoUserRole, DoneeAdmin)
admin.site.register(NgoUser, DoneeAdmin)