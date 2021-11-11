from django.db.models.functions.text import Length
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from goal.models import SDGS, Goal, GoalSave
from payment.models import Transaction, Wallet, Payment
from .models import *
from goal.models import Goal
from rest_framework.validators import UniqueValidator
import datetime


class UserRegSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'image']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id','donee_notification', 'account_activity', 'donee_activity', 'achieved_goals', 'new_followers', 'NGO_role_assign','user']


class ProfileSDGSSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="sdgs.title")
    sdgs_id = serializers.CharField(source="sdgs.id")
    thumbnail = serializers.ImageField(source="sdgs.thumbnail")
    class Meta:
        model = ProfileSDGS
        fields = ('sdgs_id', 'title', 'thumbnail')


class ProfileSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username")
    profile_username = serializers.CharField(source="username")
    profile_image = serializers.ImageField(source="image")
    ngo_username = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = ('id', 'profile_username', 'profile_image', 'profile_type', 'user_username','ngo_username')

    def get_ngo_username(self, obj):
        if obj.profile_type == 'DONEE':
            get_ngo=Profile.objects.get(id= obj.ngo_profile_id)
            return get_ngo.username
        else :
            return obj.username


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ('amount', 'profile', 'type')


class SavedGoalSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = Goal
        fields = [ 'id','title','slug', 'short_description', 'image',
                  'profile', 'status']


class SponsoredGoalSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = Goal
        fields = ['id', 'title','slug', 'short_description', 'image',
                  'profile', 'status']


class UserPaymentSerializer(serializers.ModelSerializer):
    goal = SponsoredGoalSerializer()

    class Meta:
        model = Payment
        fields = ('goal', 'user')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    from goal.serializers import GoalListSerializer, GoalSaveSerializer
    donee_notification = serializers.BooleanField(write_only=True)
    account_activity = serializers.BooleanField(write_only=True)
    donee_activity = serializers.BooleanField(write_only=True)
    achieved_goals = serializers.BooleanField(write_only=True)
    new_followers = serializers.BooleanField(write_only=True)
    NGO_role_assign = serializers.BooleanField(write_only=True)
    total_supported_goals = serializers.CharField(read_only=True)
    user_notification = NotificationSerializer(many=True, read_only=True)
    user_profile = ProfileSerializer(read_only=True)
    user_payment = UserPaymentSerializer(read_only=True, many=True)
    goalsave_user = GoalSaveSerializer(many=True, read_only=True)





    class Meta:
        model = User
        model_fields = ['username', 'full_name', 'country', 'phone_number', 'bio', 'image', 'user_notification', 'goalsave_user',
                        'total_donated_amount', 'total_follow_count', 'total_following_count']
        extra_fields = ['donee_notification', 'account_activity', 'donee_activity', 'achieved_goals', 'new_followers',
                        'NGO_role_assign', 'user_profile', 'user_payment', 'total_supported_goals']
        fields = model_fields + extra_fields



    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['country'] = CountrySerializer(instance.country).data
        return rep
   

    def update(self, instance, validated_data):
        donee_notification = validated_data.pop('donee_notification')
        account_activity = validated_data.pop('account_activity')
        donee_activity = validated_data.pop('donee_activity')
        achieved_goals = validated_data.pop('achieved_goals')
        new_followers = validated_data.pop('new_followers')
        NGO_role_assign = validated_data.pop('NGO_role_assign')
        notification_obj = Notification.objects.filter(user = self.context['request'].user)
        if notification_obj:
            notification_obj.update(donee_notification = donee_notification,
                                    account_activity = account_activity,
                                    donee_activity = donee_activity,
                                    achieved_goals = achieved_goals,
                                    new_followers = new_followers,
                                    NGO_role_assign = NGO_role_assign,
                                    modified_by = self.context['request'].user.id,
                                    modified_at = timezone.now())
        else:
            Notification.objects.create(donee_notification = donee_notification,
                                    account_activity = account_activity,
                                    donee_activity = donee_activity,
                                    achieved_goals = achieved_goals,
                                    new_followers = new_followers,
                                    NGO_role_assign = NGO_role_assign,
                                    user = self.context['request'].user,
                                    created_by=self.context['request'].user.id)
        validated_data.update({"modified_at": timezone.now(), "is_modified": True})
        return super().update(instance, validated_data)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'name')


class DonorProfileSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    total_supported_goals = serializers.CharField(read_only=True)
    user_payment = UserPaymentSerializer(read_only=True, many=True)

    class Meta:
        model = User
        model_fields = ['username', 'full_name', 'country', 'phone_number', 'bio', 'image',
                        'total_donated_amount', 'total_supported_goals', 'user_payment', 'total_follow_count','total_following_count' ]
        fields = model_fields


class DoneeAndNGOProfileSerializer(serializers.ModelSerializer):
    from goal.serializers import ProfileGoalSerializer
    total_donee_count = serializers.SerializerMethodField('_get_total_donee_count')
    total_donor = serializers.CharField(read_only=True)
    total_completed_goals = serializers.CharField(read_only=True)
    country = CountrySerializer(read_only=True)
    profile_goal = ProfileGoalSerializer(read_only=True, many=True)

    class Meta:
        model = Profile
        fields = '__all__'
        extra_fields = ['total_donor', 'total_completed_goals', 'total_donee_count']

    def _get_total_donee_count(self, obj):
        total_donee = 0
        query=Profile.objects.filter(ngo_profile_id=obj.id)

        if query:
            total_donee=len(query)
            return total_donee

        else:
            return total_donee


class DoneeAndNgoProfileCreateUpdateSerializer(serializers.ModelSerializer):
    from goal.serializers import ProfileGoalSerializer
    total_donee_count = serializers.SerializerMethodField('_get_total_donee_count')
    total_goal_count = serializers.SerializerMethodField('_get_total_goal_count')
    donee_notification = serializers.BooleanField(write_only=True)
    account_activity = serializers.BooleanField(write_only=True)
    donee_activity = serializers.BooleanField(write_only=True)
    achieved_goals = serializers.BooleanField(write_only=True)
    new_followers = serializers.BooleanField(write_only=True)
    NGO_role_assign = serializers.BooleanField(write_only=True)
    profile_notification = NotificationSerializer(many=True, read_only=True)
    profile_wallet = WalletSerializer(many=True, read_only=True)
    profile_goal = ProfileGoalSerializer(read_only=True, many=True)
    profile_sdgs = ProfileSDGSSerializer(many=True, read_only=True)
    sdgs = serializers.PrimaryKeyRelatedField(queryset=SDGS.objects.all(), many=True, write_only=True)
    total_donor = serializers.CharField(read_only=True)
    total_completed_goals = serializers.CharField(read_only=True)


    class Meta:
        model = Profile
        fields = '__all__'
        extra_fields = ['donee_notification', 'account_activity', 'donee_activity', 'achieved_goals', 'new_followers',
                        'NGO_role_assign', 'sdgs', 'total_donor', 'total_completed_goals']
        read_only_fields = ('user', 'plan_id', 'view_count', 'is_approved', 'invitation_id', 'profile_wallet', 'total_donee_count', 'total_goal_count')

    def _get_total_goal_count(self, obj):
            total_goal = 0
            total_donee_goal = 0
            total_ngo_goal = 0
            query=Profile.objects.filter(ngo_profile_id=obj.id)
            ngo_goal_query=Goal.objects.filter(profile=obj)

            for ngo_goal in ngo_goal_query:
                if ngo_goal.total_amount==ngo_goal.paid_amount:
                    total_ngo_goal+=1

            for donee_obj in query:
                donee_obj_goal_query=Goal.objects.filter(profile=donee_obj)

                if donee_obj_goal_query:
                    for donee_goal in donee_obj_goal_query:
                        if donee_goal.total_amount==donee_goal.paid_amount:
                            total_donee_goal+=1
            total_goal = total_ngo_goal + total_donee_goal
            return total_goal


    def _get_total_donee_count(self, obj):
        total_donee = 0
        query=Profile.objects.filter(ngo_profile_id=obj.id)

        if query:
            total_donee=len(query)
            return total_donee

        else:
            return total_donee

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['country'] = CountrySerializer(instance.country).data
        return rep

    def create(self, validated_data):
        donee_notification = validated_data.pop('donee_notification')
        account_activity = validated_data.pop('account_activity')
        donee_activity = validated_data.pop('donee_activity')
        achieved_goals = validated_data.pop('achieved_goals')
        new_followers = validated_data.pop('new_followers')
        NGO_role_assign = validated_data.pop('NGO_role_assign')
        sdgs = validated_data.pop('sdgs')
        profile_instance = Profile.objects.create(**validated_data, user=self.context['request'].user)
        if sdgs:
            for sdgs_id in sdgs:
                ProfileSDGS.objects.create(sdgs=sdgs_id, profile=profile_instance, created_by=self.context['request'].user.id)
        Notification.objects.create(donee_notification=donee_notification,
                                    account_activity=account_activity,
                                    donee_activity=donee_activity,
                                    achieved_goals=achieved_goals,
                                    new_followers=new_followers,
                                    NGO_role_assign=NGO_role_assign,
                                    user=self.context['request'].user,
                                    profile=profile_instance,
                                    created_by=self.context['request'].user.id)
        return profile_instance

    def update(self, instance, validated_data):
        donee_notification = validated_data.pop('donee_notification')
        account_activity = validated_data.pop('account_activity')
        donee_activity = validated_data.pop('donee_activity')
        achieved_goals = validated_data.pop('achieved_goals')
        new_followers = validated_data.pop('new_followers')
        NGO_role_assign = validated_data.pop('NGO_role_assign')
        validated_data.update({"user": self.context['request'].user})
        Notification.objects.filter(profile=instance).update(donee_notification=donee_notification,
                                account_activity=account_activity,
                                donee_activity=donee_activity,
                                achieved_goals=achieved_goals,
                                new_followers=new_followers,
                                NGO_role_assign=NGO_role_assign,
                                modified_by=self.context['request'].user.id,
                                modified_at=timezone.now())
        return super().update(instance, validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        # The default result (access/refresh tokens)
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        # Custom data you want to include
        try:
            user_profile = ProfileSerializer(self.user.user_profile).data
        except User.user_profile.RelatedObjectDoesNotExist:
            user_profile = None
        data.update({'is_account_created': self.user.is_modified, 'user_profile': user_profile})
        # and everything else you want to send in the response
        return data


class VerifyInvitationSerializer(serializers.Serializer):
   
   check_id = serializers.CharField(max_length=10)
   

class UserFollowUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserFollow
        fields = '__all__'    


class UserFollowProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileFollow
        fields = '__all__'



class InNgoDoneeInfoSerializer(serializers.ModelSerializer):
    total_donee_count = serializers.SerializerMethodField('_get_total_donee_count')
    total_active_count = serializers.SerializerMethodField('_get_total_active_count')
    total_inactive_count = serializers.SerializerMethodField('_get_total_inactive_count')


    class Meta:
        model = Profile
        fields = ['total_donee_count','total_active_count','total_inactive_count']


    def _get_total_active_count(self, obj):
        total_active = 0

        query=Profile.objects.filter(ngo_profile_id=obj.id).filter(is_active=True)
        if query:
            total_active= len(query)

        return total_active


    def _get_total_inactive_count(self, obj):
        total_inactive = 0

        query=Profile.objects.filter(ngo_profile_id=obj.id).filter(is_active=False)
        if query:
            total_inactive= len(query)

        return total_inactive


    def _get_total_donee_count(self, obj):
        total_donee = 0
        query=Profile.objects.filter(ngo_profile_id=obj.id)

        if query:
            total_donee=len(query)
            return total_donee

        else:
            return total_donee




class InNgoDoneeListSerializer(serializers.ModelSerializer):
    total_donee_wallet = serializers.SerializerMethodField('_get_total_donee_wallet')
    total_goal_count = serializers.SerializerMethodField('_get_total_goal_count')

    class Meta:
        model = Profile
        fields = ['id','image','total_goal_count','full_name','is_active','total_donee_wallet']


    def _get_total_goal_count(self, obj):

        total_goal= 0
        donee_obj_goal_query=Goal.objects.filter(profile=obj)
        if donee_obj_goal_query:
            for donee_goal in donee_obj_goal_query:
                if donee_goal.total_amount==donee_goal.paid_amount:
                    total_goal+=1
        return total_goal




    def _get_total_donee_wallet(self, obj):
        total_donee_wallet=0
        donee_wallet=Wallet.objects.filter(profile=obj)

        if donee_wallet:

            for wallet in donee_wallet:
                total_donee_wallet=wallet.amount

        return total_donee_wallet


class DashboardAppSerializer(serializers.ModelSerializer):
    from goal.serializers import ProfileGoalSerializer
    total_donee_count = serializers.SerializerMethodField('_get_total_donee_count')
    total_active_goals = serializers.SerializerMethodField('_get_total_active_goals')
    total_completed_goals = serializers.SerializerMethodField('_get_total_completed_goals')
    total_donations = serializers.SerializerMethodField('_get_total_donations')
    total_collected = serializers.SerializerMethodField('_get_total_collected')
    total_30_days_raised = serializers.SerializerMethodField('_get_total_30_days_raised')



    class Meta:
        model = Profile
        fields = ['total_active_goals','total_completed_goals','total_donee_count','view_count','total_donations','total_collected','total_30_days_raised']


    def _get_total_completed_goals(self, obj):
        total_goal = 0
        total_donee_goal = 0
        total_ngo_goal = 0
        query=Profile.objects.filter(ngo_profile_id=obj.id)
        ngo_goal_query=Goal.objects.filter(profile=obj)

        for ngo_goal in ngo_goal_query:
            if ngo_goal.total_amount==ngo_goal.paid_amount:
                total_ngo_goal+=1

        for donee_obj in query:
            donee_obj_goal_query=Goal.objects.filter(profile=donee_obj)

            if donee_obj_goal_query:
                for donee_goal in donee_obj_goal_query:
                    if donee_goal.total_amount==donee_goal.paid_amount:
                        total_donee_goal+=1
        total_goal = total_ngo_goal + total_donee_goal
        return total_goal



    def _get_total_donations(self, obj):
        total_goal_donations = 0
        donee_goal_donations = 0
        ngo_goal_donations = 0
        query=Profile.objects.filter(ngo_profile_id=obj.id)
        ngo_goal_query=Goal.objects.filter(profile=obj)

        for ngo_goal in ngo_goal_query:
            ngo_donation_query=Transaction.objects.filter(payment__goal=ngo_goal)
            if ngo_donation_query:
                for don in ngo_donation_query:
                    ngo_goal_donations+=1

        for donee_obj in query:
            donee_obj_goal_query=Goal.objects.filter(profile=donee_obj)

            if donee_obj_goal_query:
                for donee_goal in donee_obj_goal_query:
                    donee_donation_query=Transaction.objects.filter(payment__goal=donee_goal)

                    if donee_donation_query:
                        for dona in donee_donation_query:
                            donee_goal_donations+=1
        total_goal_donations = ngo_goal_donations + donee_goal_donations
        return total_goal_donations


    def _get_total_active_goals(self, obj):
        total_goal1 = 0
        total_donee_goal1 = 0
        total_ngo_goal1 = 0
        query1=Profile.objects.filter(ngo_profile_id=obj.id)
        ngo_goal_query1=Goal.objects.filter(profile=obj)

        for ngo_goal1 in ngo_goal_query1:
            if ngo_goal1.status=='ACTIVE':
                total_ngo_goal1+=1

        for donee_obj1 in query1:
            donee_obj_goal_query1=Goal.objects.filter(profile=donee_obj1)

            if donee_obj_goal_query1:
                for donee_goal1 in donee_obj_goal_query1:
                    if donee_goal1.status=='ACTIVE':
                        total_donee_goal1+=1
        total_goal1 = total_ngo_goal1 + total_donee_goal1
        return total_goal1




    def _get_total_donee_count(self, obj):
        total_donee = 0
        query=Profile.objects.filter(ngo_profile_id=obj.id)

        if query:
            total_donee=len(query)
            return total_donee

        else:
            return total_donee


    def _get_total_collected(self, obj):
        total_ngo_wallet=0
        total_donee_wallet=0
        query=Profile.objects.filter(ngo_profile_id=obj.id)
        ngo_wallet_query=Wallet.objects.filter(profile=obj)

        if ngo_wallet_query:
            for wallet in ngo_wallet_query:
                total_ngo_wallet=wallet.amount

        for donee_wallet in query:
            donee_wallet_query=Wallet.objects.filter(profile=donee_wallet)
            if donee_wallet_query:
                for wallet in donee_wallet_query:

                    total_donee_wallet+=wallet.amount

        return total_ngo_wallet+total_donee_wallet



    def _get_total_30_days_raised(self, obj):
        total_donations = 0
        donee_donations = 0
        ngo_donations = 0
        payment1= 0
        payment2= 0
        today = datetime.date.today()
        thirty_days_ago = today - datetime.timedelta(days=30)
        query=Profile.objects.filter(ngo_profile_id=obj.id)
        ngo_goal_query=Goal.objects.filter(profile=obj)



        for ngo_goal in ngo_goal_query:
            ngo_donation_query=Transaction.objects.filter(payment__goal=ngo_goal).filter(payment_updated_at__gte=thirty_days_ago)
            if ngo_donation_query:

                for don in ngo_donation_query:
                    payment1=don.payment
                    ngo_donations+=payment1.amount

        for donee_obj in query:
            donee_obj_goal_query=Goal.objects.filter(profile=donee_obj)

            if donee_obj_goal_query:
                for donee_goal in donee_obj_goal_query:
                    donee_donation_query=Transaction.objects.filter(payment__goal=donee_goal).filter(payment_updated_at__gte=thirty_days_ago)

                    if donee_donation_query:
                        for dona in donee_donation_query:
                            payment2=don.payment
                            donee_donations+=payment2.amount
        total_donations = ngo_donations + donee_donations
        return total_donations
class InvitationSerializer(serializers.Serializer):
    emails = serializers.ListField(child=serializers.EmailField(), write_only=True)
    invitation_link = serializers.CharField(write_only=True)


class EndorsedGoalsInNgoAPIViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Goal
        fields = ['id','image','title','slug']

