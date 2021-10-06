from django.contrib import admin
from Donee.admin import DoneeAdmin
from goal.models import SDGS, Setting, Goal

# Register your models here.
admin.site.register(SDGS, DoneeAdmin)
admin.site.register(Setting, DoneeAdmin)
admin.site.register(Goal, DoneeAdmin)
