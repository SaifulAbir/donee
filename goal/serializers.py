from rest_framework import serializers
from .models import *


class SDGSSerializer(serializers.ModelSerializer):
    class Meta:
        model = SDGS
        fields = ('id', 'title', 'thumbnail', 'status')


class GoalSerializer(serializers.ModelSerializer):
    sdgs = serializers.PrimaryKeyRelatedField(queryset=SDGS.objects.all(), many=True, write_only=True)
    media = serializers.ListField(child=serializers.FileField(), write_only=True)

    class Meta:
        model = Goal
        fields = ['title', 'short_description', 'full_description', 'buying_item', 'online_source_url',
                  'unit_cost', 'total_unit', 'total_amount', 'profile', 'status', 'pgw_amount',
                  'ngo_amount', 'platform_amount', 'sdgs', 'media']
        read_only_fields = ('total_amount', 'status', 'pgw_amount', 'ngo_amount', 'platform_amount')

    def create(self, validated_data):
        sdgs = validated_data.pop('sdgs')
        media = validated_data.pop('media')
        setting_obj = Setting.objects.first()
        total_cost = validated_data.get('unit_cost') * validated_data.get('total_unit')
        pgw_amount = (setting_obj.pgw * total_cost) / 100
        ngo_amount = (setting_obj.ngo * total_cost) / 100
        platform_amount = (setting_obj.platform * total_cost) / 100
        total_amount = pgw_amount + ngo_amount + platform_amount
        goal_instance = Goal.objects.create(**validated_data, pgw_amount=pgw_amount,
                                            created_by=self.context['request'].user.id,
                                            ngo_amount=ngo_amount,
                                            platform_amount=platform_amount,
                                            total_amount=total_amount)
        if sdgs:
            for sdgs_obj in sdgs:
                GoalSDGS.objects.create(sdgs=sdgs_obj, goal=goal_instance,
                                        created_by=self.context['request'].user.id)
        if media:
            for media_file in media:
                file_type = media_file.content_type.split('/')[0]
                Media.objects.create(goal=goal_instance, type=file_type, file=media_file, status="COMPLETE",
                                     created_by=self.context['request'].user.id)
        return goal_instance