from rest_framework import serializers
from .models import *


class SDGSSerializer(serializers.ModelSerializer):
    class Meta:
        model = SDGS
        fields = ('id', 'title', 'thumbnail', 'status')


class GoalSerializer(serializers.ModelSerializer):
    sdgs = serializers.PrimaryKeyRelatedField(queryset=SDGS.objects.all(), many=True)
    media = serializers.ListField(child=serializers.FileField(), write_only=True)

    class Meta:
        model = Goal
        fields = ['title', 'short_description', 'full_description', 'buying_item', 'online_source_url',
                  'unit_cost', 'total_unit', 'profile_id']
        extra_fields = ['sdgs', 'media']
        read_only_fields = ('total_amount', 'status',)

    # def create(self, validated_data):
    #     sdgs = validated_data.pop('sdgs')
    #     media = validated_data.pop('media')
    #     if sdgs:
    #         pass
    #     if media:
    #         pass
    #     goal_instance = Goal.objects.create(**validated_data, created_by=self.context['request'].user)
    #     return goal_instance