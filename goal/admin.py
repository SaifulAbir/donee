from django.contrib import admin
from Donee.admin import DoneeAdmin
from goal.models import SDGS

# Register your models here.
admin.site.register(SDGS, DoneeAdmin)
