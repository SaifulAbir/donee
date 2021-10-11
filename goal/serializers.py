from rest_framework import serializers

from user.serializers import ProfileSerializer
from .models import *


class SDGSSerializer(serializers.ModelSerializer):
    class Meta:
        model = SDGS
        fields = ('id', 'title', 'thumbnail', 'status')


class GoalSDGSSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="sdgs.title")
    class Meta:
        model = GoalSDGS
        fields = ('title', )


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['type', 'file', 'status']


class GoalListSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = Goal
        fields = ['title','slug', 'short_description', 'buying_item', 'online_source_url', 'image',
                  'total_amount', 'profile', 'status']


class GoalSerializer(serializers.ModelSerializer):
    sdgs = serializers.PrimaryKeyRelatedField(queryset=SDGS.objects.all(), many=True, write_only=True)
    media = serializers.ListField(child=serializers.FileField(), write_only=True)
    goal_sdgs = GoalSDGSSerializer(many=True, read_only=True)
    goal_media = MediaSerializer(many=True, read_only=True)

    class Meta:
        model = Goal
        fields = ['title', 'short_description', 'full_description', 'buying_item', 'online_source_url', 'image',
                  'unit_cost', 'total_unit', 'total_amount', 'profile', 'status', 'pgw_amount',
                  'ngo_amount', 'platform_amount', 'sdgs', 'media', 'goal_sdgs', 'goal_media']
        read_only_fields = ('total_amount', 'status', 'pgw_amount', 'ngo_amount', 'platform_amount','slug','pgw_percentage','ngo_percentage','platform_percentage')

    def create(self, validated_data):
        sdgs = validated_data.pop('sdgs')
        media = validated_data.pop('media')
        setting_obj = Setting.objects.first()
        total_cost = validated_data.get('unit_cost') * validated_data.get('total_unit')
        pgw_amount = (setting_obj.pgw * total_cost) / 100
        ngo_amount = (setting_obj.ngo * total_cost) / 100
        platform_amount = (setting_obj.platform * total_cost) / 100
        total_amount = pgw_amount + ngo_amount + platform_amount + total_cost
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



class SingleCatagorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalSDGS
        fields ='__all__'
        
    def to_representation(self, instance):
        rep = super(SingleCatagorySerializer, self).to_representation(instance)
        rep['sdgs-title'] = instance.sdgs.title
        rep['goal-title'] = instance.goal.title
        rep['slug'] = instance.goal.slug
        rep['image'] = instance.goal.image.url
        rep['profile'] = instance.goal.profile.username
        return rep