from rest_framework import serializers
from payment.models import Payment
from user.serializers import ProfileSerializer, UserSerializer
from .models import *


class SDGSSerializer(serializers.ModelSerializer):

    class Meta:
        model = SDGS
        fields = ('id', 'title', 'thumbnail', 'status',)


class GoalSDGSSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="sdgs.title")
    class Meta:
        model = GoalSDGS
        fields = ('title', )


class GoalPaymentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Payment
        fields = ('user', )


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'type', 'file', 'status']


class GoalListSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    class Meta:
        model = Goal
        fields = ['id', 'title','slug', 'short_description', 'buying_item', 'online_source_url', 'image',
                  'total_amount', 'profile', 'status','is_liked','total_like_count','total_comment_count','is_saved']

    def get_is_liked(self,obj):
        if self.context['request'].user.is_anonymous :
            return False
        else:
            likes = Like.objects.filter(goal = obj,is_like = True,user=self.context['request'].user.id)
            if likes.exists():
                return True
            else:
                return False
    def get_is_saved(self,obj):
        if self.context['request'].user.is_anonymous :
            return False
        else:
            saves = GoalSave.objects.filter(goal = obj,is_saved = True,user=self.context['request'].user.id)
            if saves.exists():
                return True
            else:
                return False



class GoalLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = ['goal']


class GoalCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['goal','text']

class GoalCommentCreateSerializer(serializers.ModelSerializer):

    # profile_username = serializers.CharField(source="profile.username", read_only=True)

    class Meta: 
        model = Comment
        fields = ['goal','text', 'user', 'profile']
        read_only_fields = ('user', 'profile')
        

    def create(self, validated_data):
        
        # if Profile.objects.filter(user= self.context['request'].user).exists():
            
        comment_instance = Comment.objects.create(**validated_data, user=self.context['request'].user,
                                    created_by=self.context['request'].user.id)
        
        return comment_instance
    
    



class GoalCommentGetSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(source='user.image')
    
    class Meta:
        model = Comment
        fields = ['user','text','profile_image','created_at']

    def to_representation(self, instance):
        rep = super(GoalCommentGetSerializer, self).to_representation(instance)
        rep['user'] = instance.user.full_name
        return rep


class PopularGoalSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    payment_count = serializers.CharField(read_only=True)
    percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = Goal
        fields = ['id', 'title', 'slug', 'short_description', 'image', 'paid_amount',
                  'profile', 'payment_count', 'total_amount', 'percentage']


class ProfileGoalSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField('get_videos')

    def get_videos(self, goal):
        queryset = Media.objects.filter(type="video", goal=goal)
        serializer = MediaSerializer(instance=queryset, many=True)
        return serializer.data

    class Meta:
        model = Goal
        fields = ['id', 'title', 'slug', 'image', 'media']


class GoalSaveSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoalSave
        fields = ['goal']



class GoalSerializer(serializers.ModelSerializer):
    sdgs = serializers.PrimaryKeyRelatedField(queryset=SDGS.objects.all(), many=True, write_only=True)
    media = serializers.ListField(child=serializers.FileField(), write_only=True)
    goal_sdgs = GoalSDGSSerializer(many=True, read_only=True)
    goal_media = MediaSerializer(many=True, read_only=True)
    profile_username = serializers.CharField(source="profile.username",read_only=True)
    #ngo_username = serializers.CharField(source="profile",read_only=True)
    profile_image = serializers.ImageField(source="profile.image",read_only=True)
    ngo_username = serializers.SerializerMethodField()
    goal_comment = GoalCommentGetSerializer(many=True,read_only=True)
    goal_likes = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    donor_count = serializers.CharField(read_only=True)
    goal_payment = GoalPaymentSerializer(read_only=True, many=True)



    class Meta:
        model = Goal
        fields = ['id', 'title', 'short_description', 'full_description', 'buying_item', 'online_source_url', 'image', 'slug',
                  'unit_cost', 'total_unit', 'total_amount', 'profile','profile_username','ngo_username',
                  'profile_image','status', 'pgw_amount', 'paid_amount', 'donor_count', "goal_payment",
                  'ngo_amount', 'platform_amount', 'sdgs', 'media', 'goal_sdgs', 'goal_media','goal_likes','is_liked','goal_comment','is_saved']
        read_only_fields = ('ngo_username','total_amount', 'status', 'pgw_amount', 'slug', 'ngo_amount',
                            'platform_amount','slug','pgw_percentage','ngo_percentage','platform_percentage',
                            'profile_username','profile_image','total_like_count','total_comment_count', 'payment_count')


    def get_ngo_username(self, obj):
        if obj.profile.profile_type == 'DONEE':
            get_ngo=Profile.objects.get(id= obj.profile.ngo_profile_id)
            return get_ngo.username
        else :
            return obj.profile.username

    def get_goal_likes(self,obj):
       likes = Like.objects.filter(goal = obj,is_like = True).count()
       return likes

    def get_is_liked(self,obj):
        if self.context['request'].user.is_anonymous :
            return False
        else:
            likes = Like.objects.filter(goal = obj,is_like = True,user=self.context['request'].user.id)
            if likes.exists():
                return True
            else:
                return False

    def get_is_saved(self,obj):
        if self.context['request'].user.is_anonymous :
            return False
        else:
            saves = GoalSave.objects.filter(goal = obj,is_saved = True,user=self.context['request'].user.id)
            if saves.exists():
                return True
            else:
                return False

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
    image = serializers.ImageField(source='goal.image',read_only=True)
    ngo_username = serializers.SerializerMethodField()
    profile_username = serializers.CharField(source='goal.profile',read_only=True)
    profile_image = serializers.ImageField(source="goal.profile.image",read_only=True)

    class Meta:
        model = GoalSDGS
        fields ='__all__'

    def get_ngo_username(self, obj):
        if obj.goal.profile.profile_type == 'DONEE':
            get_ngo=Profile.objects.get(id= obj.goal.profile.ngo_profile_id)
            return get_ngo.username
        else :
            return obj.goal.profile.username

    def to_representation(self, instance):
        rep = super(SingleCatagorySerializer, self).to_representation(instance)
        rep['sdgs_title'] = instance.sdgs.title
        rep['goal_title'] = instance.goal.title
        rep['slug'] = instance.goal.slug
        rep['total_like_count'] = instance.goal.total_like_count
        rep['total_comment_count'] = instance.goal.total_comment_count
        return rep


class SearchSerializer(serializers.Serializer):
    uid = serializers.CharField()
    title = serializers.CharField()
    type = serializers.CharField()
    img = serializers.CharField(required=False)