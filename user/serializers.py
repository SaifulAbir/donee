import decimal
from django.core.mail import send_mail
from django.db.models.functions.text import Length
from rest_framework import serializers, status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from goal.models import SDGS, Goal, GoalSave
from notification.models import LiveNotification
from payment.models import Transaction, Wallet, Payment, Distribution
from .models import *
from goal.models import Goal
from rest_framework.validators import UniqueValidator
import datetime
from django.db.models.functions import Extract
from itertools import zip_longest
from rest_framework.response import Response
from django.conf import settings
from django.template.loader import render_to_string

from .utils import get_current_host


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
        user.is_active = False
        user.save()
        email_list = validated_data['email']
        subject = "Account Verification"
        code = user.verification_id
        verification_link = '{}/verifyuser/id={}'.format(get_current_host(self.context.get("request")), code)
        html_message = render_to_string('verification_email.html', {'verification_link':verification_link })
        
        send_mail(
            subject=subject,
            message=None,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email_list],
            html_message=html_message
        )
        
        return user

class UserSocialRegSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ['email', 'social_status']


    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['email'])
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
        model_fields = ['id', 'username', 'full_name', 'country', 'phone_number', 'bio', 'image', 'user_notification', 'goalsave_user',
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
        model_fields = ['id', 'username', 'full_name', 'country', 'phone_number', 'bio', 'image',
                        'total_donated_amount', 'total_supported_goals', 'user_payment', 'total_follow_count','total_following_count' ]
        fields = model_fields


class DoneeAndNGOProfileSerializer(serializers.ModelSerializer):
    from goal.serializers import ProfileGoalSerializer
    is_followed = serializers.SerializerMethodField('_get_is_followed')
    total_donee_count = serializers.SerializerMethodField('_get_total_donee_count')
    total_goal_count = serializers.SerializerMethodField('_get_total_goal_count')
    total_donor = serializers.CharField(read_only=True)
    total_completed_goals = serializers.CharField(read_only=True)
    country = CountrySerializer(read_only=True)
    profile_goal = ProfileGoalSerializer(read_only=True, many=True)

    class Meta:
        model = Profile
        fields = '__all__'
        extra_fields = ['total_donor', 'total_completed_goals', 'total_donee_count','total_goal_count','is_followed']

    def _get_total_donee_count(self, obj):
        total_donee = 0
        query=Profile.objects.filter(ngo_profile_id=obj.id)

        if query:
            total_donee=len(query)
            return total_donee

        else:
            return total_donee

    def _get_is_followed(self, obj):
        
        if self.context['request'].user.is_anonymous :
            return False
        
        else: 
            query=ProfileFollow.objects.filter(follow_profile=obj.id,is_followed=True,user=self.context['request'].user.id)
            if query:
                return True
            else:
                return False


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
        if profile_instance.ngo_profile_id:
            ngo_profile = Profile.objects.get(id=profile_instance.ngo_profile_id)
            text = 'Donee @{} has accepted your request and has been added in this platform under your NGO @{}'.format(profile_instance.username, ngo_profile)
            LiveNotification.objects.create(text=text, type='DONEE_INVITATION_ACCEPT', from_user=profile_instance.user, to_user=ngo_profile.user)
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
        refresh = self.get_token(self.user)
        try:
            user_profile = ProfileSerializer(self.user.user_profile).data
        except User.user_profile.RelatedObjectDoesNotExist:
            user_profile = None
        data.update({'is_account_created': self.user.is_modified, 'user_profile': user_profile, 'user_id': self.user.id,
                     'lifetime': int(refresh.access_token.lifetime.total_seconds())})
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
    total_today_collected = serializers.SerializerMethodField('_get_today_collected')



    class Meta:
        model = Profile
        fields = ['total_active_goals','total_completed_goals','total_donee_count','view_count','total_donations','total_collected','total_30_days_raised','total_today_collected']


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
        payment3= 0
        total_amount= 0
        today = datetime.date.today()
        thirty_days_ago = today - datetime.timedelta(days=30)
        query=Profile.objects.filter(ngo_profile_id=obj.id)
        ngo_goal_query=Goal.objects.filter(profile=obj)



        for ngo_goal in ngo_goal_query:
            ngo_donation_query=Transaction.objects.filter(payment__goal=ngo_goal).filter(payment_updated_at__gte=thirty_days_ago)
            if ngo_donation_query:

                for don in ngo_donation_query:
                    ngo_distribution= Distribution.objects.get(transaction=don)
                    payment1=ngo_distribution.ngo_amount
                    ngo_donations+=payment1

        for donee_obj in query:
            donee_obj_goal_query=Goal.objects.filter(profile=donee_obj)

            if donee_obj_goal_query:
                for donee_goal in donee_obj_goal_query:
                    donee_donation_query=Transaction.objects.filter(payment__goal=donee_goal).filter(payment_updated_at__gte=thirty_days_ago)

                    if donee_donation_query:
                        for dona in donee_donation_query:
                            donee_distribution= Distribution.objects.get(transaction=dona)
                            payment2=donee_distribution.donee_amount
                            payment3=donee_distribution.ngo_amount
                            total_amount=payment2+payment3
                            donee_donations+=total_amount
        total_donations = ngo_donations + donee_donations
        return total_donations

    def _get_today_collected(self, obj):
        total_donations = 0
        donee_donations = 0
        ngo_donations = 0
        payment1= 0
        payment2= 0
        payment3= 0
        total_amount= 0
        today = datetime.date.today()
        query=Profile.objects.filter(ngo_profile_id=obj.id)
        ngo_goal_query=Goal.objects.filter(profile=obj)



        for ngo_goal in ngo_goal_query:
            ngo_donation_query=Transaction.objects.filter(payment__goal=ngo_goal).filter(payment_updated_at__date=today)
            if ngo_donation_query:

                for don in ngo_donation_query:
                    ngo_distribution= Distribution.objects.get(transaction=don)
                    payment1=ngo_distribution.ngo_amount
                    ngo_donations+=payment1

        for donee_obj in query:
            donee_obj_goal_query=Goal.objects.filter(profile=donee_obj)

            if donee_obj_goal_query:
                for donee_goal in donee_obj_goal_query:
                    donee_donation_query=Transaction.objects.filter(payment__goal=donee_goal).filter(payment_updated_at__date=today)

                    if donee_donation_query:
                        for dona in donee_donation_query:
                            donee_distribution= Distribution.objects.get(transaction=dona)
                            payment2=donee_distribution.donee_amount
                            payment3=donee_distribution.ngo_amount
                            total_amount=payment2+payment3
                            donee_donations+=total_amount
        total_donations = ngo_donations + donee_donations
        return total_donations



class InvitationSerializer(serializers.Serializer):
    emails = serializers.ListField(child=serializers.EmailField(), write_only=True)
    invitation_link = serializers.CharField(write_only=True)


class EndorsedGoalsInNgoAPIViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Goal
        fields = ['id','image','title','slug']


class UserSearchAPIViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'email']

class NgoUserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('full_name', 'image')


class RoleListSerializer(serializers.ModelSerializer):

    class Meta:
        model = NgoUserRole
        fields = ('id', 'role_type')


class NgoUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NgoUser
        fields = ('role','user','profile','is_active')
        read_only_fields = ('profile','is_active')

    def create(self, validated_data):

        profile = Profile.objects.get(user=self.context['request'].user.id)
        ngo_user_instance = NgoUser.objects.create(**validated_data,is_active=True,profile=profile,
                                    created_by=self.context['request'].user.id)

        return ngo_user_instance

class NgoUserListSerializer(serializers.ModelSerializer):

    user = NgoUserSerializer()
    role = serializers.CharField(source="role.role_type")
    class Meta:
        model = NgoUser
        fields=('id', 'user', 'role', 'is_active')


class NgoUserRoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=NgoUser
        fields=('id', 'role',)


class NgoUserStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=NgoUser
        fields=('id', 'is_active')



class DashboardMyWalletSerializer(serializers.ModelSerializer):
    from goal.serializers import ProfileGoalSerializer
    total_income = serializers.SerializerMethodField('_get_total_collected')
    today_income = serializers.SerializerMethodField('_get_today_collected')
    today_income_percentage = serializers.SerializerMethodField('_get_today_percentage')
    monthly_income = serializers.SerializerMethodField('_get_monthly_income')


    class Meta:
        model = Profile
        fields = ['total_income','today_income','today_income_percentage','monthly_income']


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


    def _get_today_collected(self, obj):
        total_donations = 0
        donee_donations = 0
        ngo_donations = 0
        payment1= 0
        payment2= 0
        payment3= 0
        total_amount= 0
        today = datetime.date.today()
        query=Profile.objects.filter(ngo_profile_id=obj.id)
        ngo_goal_query=Goal.objects.filter(profile=obj)



        for ngo_goal in ngo_goal_query:
            ngo_donation_query=Transaction.objects.filter(payment__goal=ngo_goal).filter(payment_updated_at__date=today)
            if ngo_donation_query:

                for don in ngo_donation_query:
                    ngo_distribution= Distribution.objects.get(transaction=don)
                    payment1=ngo_distribution.ngo_amount
                    ngo_donations+=payment1

        for donee_obj in query:
            donee_obj_goal_query=Goal.objects.filter(profile=donee_obj)

            if donee_obj_goal_query:
                for donee_goal in donee_obj_goal_query:
                    donee_donation_query=Transaction.objects.filter(payment__goal=donee_goal).filter(payment_updated_at__date=today)

                    if donee_donation_query:
                        for dona in donee_donation_query:
                            donee_distribution= Distribution.objects.get(transaction=dona)
                            payment2=donee_distribution.donee_amount
                            payment3=donee_distribution.ngo_amount
                            total_amount=payment2+payment3
                            donee_donations+=total_amount
        total_donations = ngo_donations + donee_donations
        return total_donations


    def _get_today_percentage(self, obj):
        total_ngo_wallet=0
        total_donee_wallet=0
        total_collected=0
        today_collected = 0
        donee_donations = 0
        ngo_donations = 0
        today_percentage = 0
        payment1= 0
        payment2= 0
        payment3= 0
        total_amount= 0
        today = datetime.date.today()
        query=Profile.objects.filter(ngo_profile_id=obj.id)
        ngo_wallet_query=Wallet.objects.filter(profile=obj)
        ngo_goal_query=Goal.objects.filter(profile=obj)

        for ngo_goal in ngo_goal_query:
            ngo_donation_query=Transaction.objects.filter(payment__goal=ngo_goal).filter(payment_updated_at__date=today)
            if ngo_donation_query:

                for don in ngo_donation_query:
                    ngo_distribution= Distribution.objects.get(transaction=don)
                    payment1=ngo_distribution.ngo_amount
                    ngo_donations+=payment1

        for donee_obj in query:
            donee_obj_goal_query=Goal.objects.filter(profile=donee_obj)

            if donee_obj_goal_query:
                for donee_goal in donee_obj_goal_query:
                    donee_donation_query=Transaction.objects.filter(payment__goal=donee_goal).filter(payment_updated_at__date=today)

                    if donee_donation_query:
                        for dona in donee_donation_query:
                            donee_distribution= Distribution.objects.get(transaction=dona)
                            payment2=donee_distribution.donee_amount
                            payment3=donee_distribution.ngo_amount
                            total_amount=payment2+payment3
                            donee_donations+=total_amount
        today_collected = ngo_donations + donee_donations

        if ngo_wallet_query:
            for wallet in ngo_wallet_query:
                total_ngo_wallet=wallet.amount

        for donee_wallet in query:
            donee_wallet_query=Wallet.objects.filter(profile=donee_wallet)
            if donee_wallet_query:
                for wallet in donee_wallet_query:
                    total_donee_wallet+=wallet.amount

        total_collected=total_ngo_wallet+total_donee_wallet
        if total_collected:
            today_percentage=(today_collected*100)/total_collected
            return today_percentage
        
        else:
            return 0



    def _get_monthly_income(self, obj):
        current_year=datetime.date.today().year
        data_list=[]
        jan=0
        feb=0
        mar=0
        apr=0
        may=0
        jun=0
        jul=0
        aug=0
        sep=0
        octo=0
        nov=0
        dec=0
        jan1=0
        feb1=0
        mar1=0
        apr1=0
        may1=0
        jun1=0
        jul1=0
        aug1=0
        sep1=0
        octo1=0
        nov1=0
        dec1=0
        query=Profile.objects.filter(ngo_profile_id=obj.id)
        ngo_goal_query=Goal.objects.filter(profile=obj)
        for ngo_goal in ngo_goal_query:
            ngo_donation_query=Transaction.objects.filter(payment__goal=ngo_goal)

            if ngo_donation_query:
                for don in ngo_donation_query:
                    ngo_year=don.payment_updated_at.year
                    ngo_month=don.payment_updated_at.month

                    if ngo_year==current_year and ngo_month==1:
                        ngo_distribution= Distribution.objects.get(transaction=don)
                        payment1=ngo_distribution.ngo_amount
                        jan+=payment1

                    if ngo_year==current_year and ngo_month==2:
                        ngo_distribution= Distribution.objects.get(transaction=don)
                        payment1=ngo_distribution.ngo_amount
                        feb+=payment1

                    if ngo_year==current_year and ngo_month==3:
                        ngo_distribution= Distribution.objects.get(transaction=don)
                        payment1=ngo_distribution.ngo_amount
                        mar+=payment1

                    if ngo_year==current_year and ngo_month==4:
                        ngo_distribution= Distribution.objects.get(transaction=don)
                        payment1=ngo_distribution.ngo_amount
                        apr+=payment1

                    if ngo_year==current_year and ngo_month==5:
                        ngo_distribution= Distribution.objects.get(transaction=don)
                        payment1=ngo_distribution.ngo_amount
                        may+=payment1

                    if ngo_year==current_year and ngo_month==6:
                        ngo_distribution= Distribution.objects.get(transaction=don)
                        payment1=ngo_distribution.ngo_amount
                        jun+=payment1

                    if ngo_year==current_year and ngo_month==7:
                        ngo_distribution= Distribution.objects.get(transaction=don)
                        payment1=ngo_distribution.ngo_amount
                        jul+=payment1

                    if ngo_year==current_year and ngo_month==8:
                        ngo_distribution= Distribution.objects.get(transaction=don)
                        payment1=ngo_distribution.ngo_amount
                        aug+=payment1

                    if ngo_year==current_year and ngo_month==9:
                        ngo_distribution= Distribution.objects.get(transaction=don)
                        payment1=ngo_distribution.ngo_amount
                        sep+=payment1

                    if ngo_year==current_year and ngo_month==10:
                        ngo_distribution= Distribution.objects.get(transaction=don)
                        payment1=ngo_distribution.ngo_amount
                        octo+=payment1

                    if ngo_year==current_year and ngo_month==11:
                        ngo_distribution= Distribution.objects.get(transaction=don)
                        payment1=ngo_distribution.ngo_amount
                        nov+=payment1

                    if ngo_year==current_year and ngo_month==12:
                        ngo_distribution= Distribution.objects.get(transaction=don)
                        payment1=ngo_distribution.ngo_amount
                        dec+=payment1


        for donee_obj in query:
            donee_goal_query=Goal.objects.filter(profile=donee_obj)
            for donee_goal in donee_goal_query:
                donee_donation_query=Transaction.objects.filter(payment__goal=donee_goal)

                if donee_donation_query:
                    for don in donee_donation_query:
                        donee_year=don.payment_updated_at.year
                        donee_month=don.payment_updated_at.month

                        if donee_year==current_year and donee_month==1:
                            donee_distribution= Distribution.objects.get(transaction=don)
                            payment2=donee_distribution.donee_amount
                            payment3=donee_distribution.ngo_amount
                            total_amount=payment2+payment3
                            jan1+=total_amount

                        if donee_year==current_year and donee_month==2:
                            donee_distribution= Distribution.objects.get(transaction=don)
                            payment2=donee_distribution.donee_amount
                            payment3=donee_distribution.ngo_amount
                            total_amount=payment2+payment3
                            feb1+=total_amount

                        if donee_year==current_year and donee_month==3:
                            donee_distribution= Distribution.objects.get(transaction=don)
                            payment2=donee_distribution.donee_amount
                            payment3=donee_distribution.ngo_amount
                            total_amount=payment2+payment3
                            mar1+=total_amount

                        if donee_year==current_year and donee_month==4:
                            donee_distribution= Distribution.objects.get(transaction=don)
                            payment2=donee_distribution.donee_amount
                            payment3=donee_distribution.ngo_amount
                            total_amount=payment2+payment3
                            apr1+=total_amount

                        if donee_year==current_year and donee_month==5:
                            donee_distribution= Distribution.objects.get(transaction=don)
                            payment2=donee_distribution.donee_amount
                            payment3=donee_distribution.ngo_amount
                            total_amount=payment2+payment3
                            may1+=total_amount

                        if donee_year==current_year and donee_month==6:
                            donee_distribution= Distribution.objects.get(transaction=don)
                            payment2=donee_distribution.donee_amount
                            payment3=donee_distribution.ngo_amount
                            total_amount=payment2+payment3
                            jun1+=total_amount

                        if donee_year==current_year and donee_month==7:
                            donee_distribution= Distribution.objects.get(transaction=don)
                            payment2=donee_distribution.donee_amount
                            payment3=donee_distribution.ngo_amount
                            total_amount=payment2+payment3
                            jul1+=total_amount

                        if donee_year==current_year and donee_month==8:
                            donee_distribution= Distribution.objects.get(transaction=don)
                            payment2=donee_distribution.donee_amount
                            payment3=donee_distribution.ngo_amount
                            total_amount=payment2+payment3
                            aug1+=total_amount

                        if donee_year==current_year and donee_month==9:
                            donee_distribution= Distribution.objects.get(transaction=don)
                            payment2=donee_distribution.donee_amount
                            payment3=donee_distribution.ngo_amount
                            total_amount=payment2+payment3
                            sep1+=total_amount

                        if donee_year==current_year and donee_month==10:
                            donee_distribution= Distribution.objects.get(transaction=don)
                            payment2=donee_distribution.donee_amount
                            payment3=donee_distribution.ngo_amount
                            total_amount=payment2+payment3
                            octo1+=total_amount

                        if donee_year==current_year and donee_month==11:
                            donee_distribution= Distribution.objects.get(transaction=don)
                            payment2=donee_distribution.donee_amount
                            payment3=donee_distribution.ngo_amount
                            total_amount=payment2+payment3
                            nov1+=total_amount

                        if donee_year==current_year and donee_month==12:
                            donee_distribution= Distribution.objects.get(transaction=don)
                            payment2=donee_distribution.donee_amount
                            payment3=donee_distribution.ngo_amount
                            total_amount=payment2+payment3
                            dec1+=total_amount

        data_list=[jan+jan1,feb+feb1,mar+mar1,apr+apr1,may+may1,jun+jun1,jul+jul1,aug+aug1,sep+sep1,octo+octo1,nov+nov1,dec+dec1]
        date=["01/01/2020","02/01/2020","03/01/2020","04/01/2020","05/01/2020","06/01/2020","07/01/2020","08/01/2020","09/01/2020","10/01/2020","11/01/2020","12/01/2020"]
        return data_list,date


class DashboardDonorSerializer(serializers.ModelSerializer):
    donors = serializers.SerializerMethodField('_get_donors_count')
    donations = serializers.SerializerMethodField('_get_donations')
    donations_amount = serializers.SerializerMethodField('_get_donations_amount')
    new_donors = serializers.SerializerMethodField('_get_new_donors')
    donors_by_country = serializers.SerializerMethodField('_get_donors_by_country')
    recent_activity = serializers.SerializerMethodField('_get_recent_activity')

    class Meta:
        model = Profile
        fields = ['donors', 'donations', 'donations_amount', 'new_donors', 'donors_by_country','recent_activity']

    
    def _get_donations(self,obj):
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


    def _get_donors_count(self,obj):
        total_unique_donors = 0
        ngo_goal_donor_count = 0
        donee_goal_donor_count = 0
        ngo_donor_list=[]
        unique_ngo_donor_list=[]
        donee_donor_list=[]
        unique_donee_donor_list=[]
        
        query=Profile.objects.filter(ngo_profile_id=obj.id)
        ngo_goal_query=Goal.objects.filter(profile=obj)
        
        for ngo_goal in ngo_goal_query:
            ngo_donation_query=Payment.objects.filter(goal=ngo_goal)
            if ngo_donation_query:
                for don in ngo_donation_query:
                    donor = don.user.id
                    ngo_donor_list.append(donor)
            
            unique_ngo_donor_list = set(ngo_donor_list)
            ngo_goal_donor_count = len(unique_ngo_donor_list)

        
        for donee_obj in query:
            donee_obj_goal_query=Goal.objects.filter(profile=donee_obj) 

            if donee_obj_goal_query:
                for goal in donee_obj_goal_query:
                    donee_donation_query=Payment.objects.filter(goal=goal)
                    if donee_donation_query:
                        for don in donee_donation_query:
                            donor=don.user.id
                            donee_donor_list.append(donor)
            
            unique_donee_donor_list = set(donee_donor_list)
            donee_goal_donor_count = len(unique_donee_donor_list)
            
        
        total_unique_donors = ngo_goal_donor_count + donee_goal_donor_count
        return total_unique_donors

    def _get_donations_amount(self,obj):
        ngo_donations_amount = 0.0
        donee_donations_amount = 0.0
        total_donations_amount = 0.0
        
        
        query=Profile.objects.filter(ngo_profile_id=obj.id)
        ngo_goal_query=Goal.objects.filter(profile=obj)
        
        for ngo_goal in ngo_goal_query:
            ngo_donation_query=Payment.objects.filter(goal=ngo_goal)
            if ngo_donation_query:
                for don in ngo_donation_query:
                    ngo_amount = don.amount
                    ngo_donations_amount = decimal.Decimal(ngo_donations_amount) + decimal.Decimal(ngo_amount)
                
                    
        for donee_obj in query:
            donee_obj_goal_query=Goal.objects.filter(profile=donee_obj) 

            if donee_obj_goal_query:
                for goal in donee_obj_goal_query:
                    donee_donation_query=Payment.objects.filter(goal=goal)
                    if donee_donation_query:
                        for don in donee_donation_query:
                            donee_amount=don.amount
                            donee_donations_amount = decimal.Decimal(donee_donations_amount) + decimal.Decimal(donee_amount)
                       
        total_donations_amount = ngo_donations_amount + donee_donations_amount  
        return total_donations_amount 

    def _get_new_donors(self, obj):
        total_new_donors = 0
        ngo_goal_donor_count = 0
        donee_goal_donor_count = 0
        ngo_donor_list=[]
        new_ngo_donor_list=[]
        donee_donor_list=[]
        new_donee_donor_list=[]
        today = datetime.date.today()
        
        query=Profile.objects.filter(ngo_profile_id=obj.id)
        ngo_goal_query=Goal.objects.filter(profile=obj)
        
        for ngo_goal in ngo_goal_query:
            ngo_donation_query=Payment.objects.filter(goal=ngo_goal, created_at= today)
            if ngo_donation_query:
                for don in ngo_donation_query:
                    donor = don.user.id
                    ngo_donor_list.append(donor)
            
            new_ngo_donor_list = set(ngo_donor_list)
            ngo_goal_donor_count = len(new_ngo_donor_list)

         

        for donee_obj in query:
            donee_obj_goal_query=Goal.objects.filter(profile=donee_obj) 

            if donee_obj_goal_query:
                for goal in donee_obj_goal_query:
                    donee_donation_query=Payment.objects.filter(goal=goal, created_at = today)
                    if donee_donation_query:
                        for don in donee_donation_query:
                            donor=don.user.id
                            donee_donor_list.append(donor)
            
            new_donee_donor_list = set(donee_donor_list)
            donee_goal_donor_count = len(new_donee_donor_list)
            
        
        total_new_donors = ngo_goal_donor_count + donee_goal_donor_count
        return total_new_donors

    def _get_donors_by_country(self, obj):
        ngo_donor_country_list=[]
        country_id_list = []
        country_name_list = []
        ngo_donor_country_count_list = []
        donee_donor_country_count_list = []
        total_donor_country_count_list = []
        donor_country_count_percentage_list = []
        donor_country_count_percentage_round_list = []
        
        query=Profile.objects.filter(ngo_profile_id=obj.id)
        ngo_goal_query=Goal.objects.filter(profile=obj)
        
        for ngo_goal in ngo_goal_query:
            ngo_donation_query=Payment.objects.filter(goal=ngo_goal)
            if ngo_donation_query:
                for don in ngo_donation_query:
                    donors = don.user.id
                    country = don.user.country
                    ngo_donor_country_list.append(country)
                
        country_list = Country.objects.all()
        for country in country_list:
            country_id_list.append(country.id)
            country_name_list.append(country.name)
        

        for country_id in country_id_list:
            ngo_count = 0
            for donor_country_id in ngo_donor_country_list:
            
                if country_id == donor_country_id:
                    
                    ngo_count +=1
            ngo_donor_country_count_list.append(ngo_count)
        
        
        for donee_obj in query:
            donee_obj_goal_query=Goal.objects.filter(profile=donee_obj) 

            if donee_obj_goal_query:
                for goal in donee_obj_goal_query:
                    donee_donation_query=Payment.objects.filter(goal=goal)
                    if donee_donation_query:
                        for don in donee_donation_query:
                            donor=don.user.id
                            country = don.user.country.id
                    ngo_donor_country_list.append(country)
                    
        
        for country_id in country_id_list:
            donee_count = 0
            for donor_country_id in ngo_donor_country_list:
            
                if country_id == donor_country_id:
                    donee_count +=1
            donee_donor_country_count_list.append(donee_count)
        
        total_donor_country_count_list = list(map(sum, zip_longest(ngo_donor_country_count_list, donee_donor_country_count_list, fillvalue=0)))
        total_donors = sum(total_donor_country_count_list)
        if total_donors:
            donor_country_count_percentage_list = [percentage_donors/total_donors * 100 for percentage_donors in total_donor_country_count_list]
            donor_country_count_percentage_round_list = ['%.2f' % elem for elem in donor_country_count_percentage_list]
            return donor_country_count_percentage_round_list, country_name_list
        else:
            return [0],country_name_list

        

    def _get_recent_activity(self,obj):
        ngo_donor_list=[]
        today = datetime.date.today()
        seven_days_ago = today - datetime.timedelta(days=7)

        query=Profile.objects.filter(ngo_profile_id=obj.id)
        ngo_goal_query=Goal.objects.filter(profile=obj)
        ngo = obj.full_name
        for ngo_goal in ngo_goal_query:
            ngo_donation_query=Payment.objects.filter(goal=ngo_goal, status="PAID").filter(created_at__gte=seven_days_ago)
            
            if ngo_donation_query:
                for don in ngo_donation_query:
                    donor = don.user.full_name
                    created_at = don.created_at
                    amount = don.amount
                    
                    ngo_dict = {'donor_fullname': donor, 'created_at': created_at, 'amount': amount , 'ngo_fullname': ngo}
                    ngo_donor_list.append(ngo_dict)

        for donee_obj in query:
            donee_obj_goal_query=Goal.objects.filter(profile=donee_obj) 
            donee = donee_obj.full_name

            if donee_obj_goal_query:
                for goal in donee_obj_goal_query:
                    donee_donation_query=Payment.objects.filter(goal=goal, status="PAID").filter(created_at__gte=seven_days_ago)
                    if donee_donation_query:
                        for don in donee_donation_query:
                            donor=don.user.full_name
                            donor = don.user.full_name
                            created_at = don.created_at
                            amount = don.amount

                            donee_dict = {'donor_fullname': donor, 'created_at': created_at, 'amount': amount , 'donee_fullname': donee}
                            ngo_donor_list.append(donee_dict)

        return ngo_donor_list

class IdActiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        




        
        



                
        


        

            
        
