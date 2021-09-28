from rest_framework import serializers
from .models import *
from rest_framework.validators import UniqueValidator
from rest_framework.parsers import MultiPartParser, FormParser




class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields ="__all__"
        read_only_fields = ['pgw_amount','ngo_amount','platform_amount','total_amount','profile_id','status']