from rest_framework import serializers
from .models import *


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields ="__all__"
        read_only_fields = ['pgw_amount','ngo_amount','platform_amount','total_amount','profile_id','status']


class SDGSSerializer(serializers.ModelSerializer):
    class Meta:
        model = SDGS
        fields = ('id', 'name')