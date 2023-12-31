import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count, Q, F, Sum, Value, CharField, JSONField
from django.db.models import query
from django.db.models.functions import Concat
from django.db.models.query import Prefetch, QuerySet
from django.template.loader import render_to_string, get_template
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from notification.models import LiveNotification
from payment.models import Payment, Wallet, Transaction
from user.models import NgoUser, NgoUserRole, User, Profile, Country, Notification, ProfileFollow, UserFollow, \
    PlatformUserRole, PlatformUser
from goal.models import Goal, GoalSave
from user.serializers import DashboardDonorSerializer, NgoUserCreateSerializer, NgoUserListSerializer, \
    NgoUserRoleUpdateSerializer, \
    NgoUserStatusUpdateSerializer, RoleListSerializer, UserProfileUpdateSerializer, \
    DoneeAndNgoProfileCreateUpdateSerializer, CountrySerializer, CustomTokenObtainPairSerializer, \
    DonorProfileSerializer, DoneeAndNGOProfileSerializer, UserFollowUserSerializer, UserFollowProfileSerializer, \
    InvitationSerializer, InNgoDoneeInfoSerializer, InNgoDoneeListSerializer, \
    DashboardAppSerializer, EndorsedGoalsInNgoAPIViewSerializer, UserSocialRegSerializer, UserSearchAPIViewSerializer, \
    DashboardMyWalletSerializer, IdActiveSerializer, \
    CountryCodeSerializer, PlatformDashboardSerializer, DashboardDoneeInfoSerializer, DashboardDoneeListSerializer, \
    PlatformDashboardDonorSerializer, DashboardNGOInfoSerializer, PlatformDashboardWalletInfoSerializer, \
    PlatformRoleListSerializer, PlatformUserCreateSerializer, PlatformUserListSerializer, DoneeOfTheMonthSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from user.utils import profile_view_count


class CustomTokenObtainPairView(TokenObtainPairView):
    # Replace the serializer with your custom
    serializer_class = CustomTokenObtainPairSerializer


class SocialSignupAPIView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSocialRegSerializer

    def post(self, request, *args, **kwargs):
        return super(SocialSignupAPIView, self).post(request, *args, **kwargs)


class UserUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = UserProfileUpdateSerializer

    def get_object(self):
        user = User.objects.filter(id=self.request.user.id).prefetch_related(
            Prefetch('user_notification',queryset = Notification.objects.filter(profile__isnull=True))).prefetch_related(
            Prefetch("user_payment", queryset=Payment.objects.filter(status="PAID").distinct('goal'))).annotate(
            total_supported_goals=Count(
                Concat('user_payment__user', 'user_payment__goal'),
                filter=Q(user_payment__status='PAID'),
                distinct=True
            )
        ).prefetch_related(
            Prefetch('goalsave_user', queryset=GoalSave.objects.filter(is_saved=True).distinct('goal')))
        return user.first()

    def put(self, request, *args, **kwargs):
        try:
            user = User.objects.filter(username=request.data["username"]).exclude(id=request.user.id)
            if user:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
            return self.update(request, *args, **kwargs)
        except KeyError:
            return self.update(request, *args, **kwargs)


class DonorProfileAPIView(RetrieveAPIView):
    serializer_class = DonorProfileSerializer
    permission_classes = [AllowAny, ]

    def get_object(self):
        user_id = self.kwargs['pk']
        user = User.objects.annotate(
            total_supported_goals=Count(
                Concat('user_payment__user', 'user_payment__goal'),
                filter=Q(user_payment__status='PAID'),
                distinct=True
            )
        ).prefetch_related(
            Prefetch("user_payment", queryset=Payment.objects.filter(status="PAID").distinct('goal'))).get(id=user_id)
        return user


class DoneeAndNGOProfileAPIView(RetrieveAPIView):
    serializer_class = DoneeAndNGOProfileSerializer
    permission_classes = [AllowAny, ]

    def get_object(self):
        profile_id = self.kwargs['pk']
        queryset = Profile.objects.annotate(
            total_donor=Count(
                Concat('profile_goal__goal_payment__goal', 'profile_goal__goal_payment__user'),
                filter=Q(profile_goal__goal_payment__status='PAID'),
                distinct=True
            ),
            total_completed_goals = Count(
                'profile_goal', filter=Q(profile_goal__paid_amount=F('profile_goal__total_amount'))
            )
        ).get(id=profile_id)
        profile_view_count(queryset)
        return queryset


class DoneeAndNgoProfileCreateAPIView(CreateAPIView):
    serializer_class = DoneeAndNgoProfileCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return super(DoneeAndNgoProfileCreateAPIView, self).post(request, *args, **kwargs)


class DoneeAndNgoProfileUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = DoneeAndNgoProfileCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Profile.objects.annotate(
            total_donor=Count(
                Concat('profile_goal__goal_payment__goal', 'profile_goal__goal_payment__user'),
                filter=Q(profile_goal__goal_payment__status='PAID'),
                distinct=True
            ),
            total_completed_goals = Count(
                'profile_goal', filter=Q(profile_goal__paid_amount=F('profile_goal__total_amount'))
            )
        ).get(user=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class inNgoDoneeInfoAPIView(RetrieveAPIView):
    serializer_class = InNgoDoneeInfoSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)
        payments = Payment.objects.filter(goal__profile__profile_type="DONEE",
                                          payment_transaction__payment_updated_at__gte=thirty_days_ago). \
            annotate(total_paid_amount=Sum('payment_transaction__paid_amount')).order_by('-total_paid_amount').first()
        if payments:
            goal = Goal.objects.filter(profile=payments.goal.profile).count()
            donee_of_the_month = {"profile": payments.goal.profile, "total_paid_amount": payments.total_paid_amount,
                                  "total_goal": goal}
        else:
            donee_of_the_month = {}
        donee_of_the_month = DoneeOfTheMonthSerializer(donee_of_the_month, many=False)
        return Profile.objects.filter(user=self.request.user).annotate(donee_of_the_month = Value(donee_of_the_month.data, output_field=JSONField())).first()


class inNgoDoneeListAPIView(ListAPIView):
    serializer_class = InNgoDoneeListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        ngo_obj= Profile.objects.get(user=self.request.user)
        return Profile.objects.filter(ngo_profile_id=ngo_obj.id)

       


class CountryListAPI(ListAPIView):
    queryset = Country.objects.all().order_by('name')
    serializer_class = CountrySerializer


class UserFollowUserAPI(CreateAPIView):
    serializer_class = UserFollowUserSerializer
    queryset = UserFollow.objects.all()

    def create(self, request, *args, **kwargs):
        if self.request.data =={} :
            raise ValidationError({"follow_user":'this field is required'})
        else:
            if isinstance(self.request.data['follow_user'], int):
                user = User.objects.get(id = self.request.user.id)
                follow_user = User.objects.get(id = self.request.data['follow_user'])
                check_follow = UserFollow.objects.filter(user = self.request.user.id,follow_user = self.request.data['follow_user']) #check follower user
                check_profile = Profile.objects.filter(user = self.request.user.id)
                if check_follow.exists() and check_follow.first().is_followed == True:
                    obj = check_follow.first()
                    obj.is_followed = False
                    obj.save()
                    follow_user_obj = follow_user
                    user_obj = user
                    follow_user.total_follow_count -=1
                    user.total_following_count -=1
                    print(user.total_following_count)
                    follow_user_obj.save()
                    user_obj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"follow_user":self.request.data["follow_user"],"is_followed":False,}, status=status.HTTP_200_OK)
                if check_follow.exists() and check_follow.first().is_followed == False:
                    obj = check_follow.first()
                    obj.is_followed = True
                    obj.save()
                    follow_user_obj = follow_user
                    user_obj = user
                    follow_user_obj.total_follow_count +=1
                    user_obj.total_following_count +=1
                    print(user.total_following_count)
                    follow_user_obj.save()
                    user_obj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"follow_user":self.request.data["follow_user"],"is_followed":True,}, status=status.HTTP_200_OK)

                
                else:
                    follow_user_obj = follow_user
                    user_obj = user
                    follow_user_obj.total_follow_count +=1
                    user_obj.total_following_count +=1
                    print(user.total_following_count)
                    follow_user_obj.save()
                    user_obj.save()
                    followobj= UserFollow(user = user,follow_user = follow_user,is_followed = True,created_by =user.username)
                    followobj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"follow_user":self.request.data["follow_user"],"is_followed":True,}, status=status.HTTP_201_CREATED)
            else:
                raise ValidationError({"follow_user":'must provide integer user id!'})



class UserFollowProfileAPI(CreateAPIView):
    serializer_class = UserFollowProfileSerializer
    queryset = ProfileFollow.objects.all()

    def create(self, request, *args, **kwargs):
        if self.request.data =={} :
            raise ValidationError({"follow_profile":'this field is required'})
        else:
            if isinstance(self.request.data['follow_profile'], int):
                user = User.objects.get(id = self.request.user.id)
                follow_profile = Profile.objects.get(id = self.request.data['follow_profile'])
                check_follow = ProfileFollow.objects.filter(user = self.request.user.id,follow_profile = self.request.data['follow_profile'])  #check follower user
                check_profile = Profile.objects.filter(user = self.request.user.id)
                if check_follow.exists() and check_follow.first().is_followed == True:
                    obj = check_follow.first()
                    obj.is_followed = False
                    obj.save()
                    follow_profile_obj = follow_profile
                    user_obj = user
                    follow_profile.total_follow_count -=1
                    user_obj.total_following_count -=1
                    print(user.total_following_count)
                    follow_profile_obj.save()
                    user_obj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"follow_profile":self.request.data["follow_profile"],"is_followed":False,}, status=status.HTTP_200_OK)
                if check_follow.exists() and check_follow.first().is_followed == False:
                    obj = check_follow.first()
                    obj.is_followed = True
                    obj.save()
                    follow_profile_obj = follow_profile
                    user_obj = user
                    follow_profile_obj.total_follow_count +=1
                    user_obj.total_following_count +=1
                    print(user.total_following_count)
                    follow_profile_obj.save()
                    user_obj.save()

                    # Notification
                    text = '@{} is following you'.format(user.username)
                    LiveNotification.objects.create(text=text, type='PROFILE_FOLLOW',
                                                    identifier= user_obj.id,
                                                    from_user=user, to_user=follow_profile.user)
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"follow_profile":self.request.data["follow_profile"],"is_followed":True,}, status=status.HTTP_200_OK)

            
                else:
                    follow_profile_obj = follow_profile
                    user_obj = user
                    follow_profile_obj.total_follow_count +=1
                    user_obj.total_following_count +=1
                    print(user.total_following_count)
                    follow_profile_obj.save()
                    user_obj.save()
                    followobj= ProfileFollow(user = user,follow_profile = follow_profile,is_followed = True,created_by =user.username)
                    followobj.save()

                    # Notification
                    text = '@{} is following you'.format(user.username)
                    LiveNotification.objects.create(text=text, type='PROFILE_FOLLOW', identifier= user_obj.id,
                                                    from_user=user, to_user=follow_profile.user)
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"follow_profile":self.request.data["follow_profile"],"is_followed":True,}, status=status.HTTP_201_CREATED)
            else:
                raise ValidationError({"follow_profile":'must provide integer user id!'})



class DoneeStatusUpdateAPIView(CreateAPIView):
    serializer_class = DoneeAndNGOProfileSerializer
    queryset = Profile.objects.all()

    def create(self, request, *args, **kwargs):

        if self.request.data =={}:
            raise ValidationError({"goal":'this field may not be null'
            })
        else:
            profile = Profile.objects.get(id = self.request.data['profile'])
            is_active = self.request.data['is_active']

            if profile:
                obj = profile
                obj.is_active = is_active
                obj.save()
                return Response({"id":self.request.data['profile'],"is_active":self.request.data["is_active"]})

            else:
                raise ValidationError({"profile":'this field may not be null'
            })



class EndorsedGoalsInNgoAPIView(ListAPIView):
    serializer_class = EndorsedGoalsInNgoAPIViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile=Profile.objects.get(user=self.request.user)
        donee=Profile.objects.filter(ngo_profile_id=profile.id)
        query_list=[]

        for donee_obj in donee:
            goal=Goal.objects.filter(profile=donee_obj)
            for goal_obj in goal:
                query_list.append(goal_obj)

        return query_list





class SendInvitationLink(APIView):
    @swagger_auto_schema(request_body=InvitationSerializer)
    def post(self, request, *args, **kwargs):
        invitation_serializer = InvitationSerializer(data=request.data)
        if invitation_serializer.is_valid():
            profile = Profile.objects.get(user=self.request.user)
            invitation_link = request.data.get('invitation_link')
            email_list = request.POST.getlist('emails')
            subject = "You have been invited to become donee"
            html_message = render_to_string('invitation_email.html', {'invitation_link': invitation_link, 'ngo_username': profile.username})
            send_mail(
                subject=subject,
                message=None,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=email_list,
                html_message=html_message
            )
            return Response({'message': 'Email sent successfully!'})
        return Response({'message': invitation_serializer.errors})




class DashboardAppAPIView(RetrieveAPIView):
    serializer_class = DashboardAppSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return Profile.objects.get(user=self.request.user)
        except:
            return Response({'message': 'profile is not found'})
    


class UserSearchAPIView(ListAPIView):
    serializer_class = UserSearchAPIViewSerializer

    def get_queryset(self):
        query = self.request.GET.get('query')
        profile = Profile.objects.get(user=self.request.user)
        ngo_user = NgoUser.objects.filter(profile=profile)
        user_list=User.objects.filter(~Q(user_profile__profile_type="DONEE") & ~Q(id=self.request.user.id))
        if query:
            user_list=User.objects.filter(Q(email__icontains=query) | Q(full_name__icontains=query)).\
                filter(~Q(user_profile__profile_type="DONEE") & ~Q(id=self.request.user.id) & ~Q(user_ngo_user__in=ngo_user))
        return user_list


class RoleListAPIView(ListAPIView):
    queryset = NgoUserRole.objects.filter()
    serializer_class = RoleListSerializer


class PlatformRoleListAPIView(ListAPIView):
    queryset = PlatformUserRole.objects.all()
    serializer_class = PlatformRoleListSerializer


class NgoUserCreateAPIView(CreateAPIView):
    serializer_class = NgoUserCreateSerializer


class PlatformUserCreateAPIView(CreateAPIView):
    serializer_class = PlatformUserCreateSerializer


class PlatformUserListAPIView(ListAPIView):
    serializer_class=PlatformUserListSerializer

    def get_queryset(self):
        platform_users = PlatformUser.objects.all()
        return platform_users


class NgoUserListAPIView(ListAPIView):
    serializer_class=NgoUserListSerializer

    def get_queryset(self):
        profile= Profile.objects.get(user=self.request.user)
        ngo_users = NgoUser.objects.filter(profile=profile)
        return ngo_users

class NgoUserRoleUpdateAPIView(UpdateAPIView):
    queryset=NgoUser.objects.all()
    serializer_class=NgoUserRoleUpdateSerializer

class NgoUserUpdateStatusAPIView(UpdateAPIView):
    queryset=NgoUser.objects.all()
    serializer_class= NgoUserStatusUpdateSerializer


class DashboardMyWalletAPIView(RetrieveAPIView):
    serializer_class = DashboardMyWalletSerializer

    def get_object(self):
        try:
            return Profile.objects.get(user=self.request.user)
        except:
            return Response({'message': 'profile is not found'})


class DashboardDonorsAPIView(RetrieveAPIView):
    serializer_class = DashboardDonorSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Profile.objects.get(user=self.request.user)
        
        
class IdActiveAPIView(APIView):
    serializer_class = IdActiveSerializer
    permission_classes = [AllowAny, ]

    def get(self,  *args, **kwargs):
        verification = kwargs.get('verification')
        query_user=User.objects.get(verification_id=verification)
        query_user.is_active=True
        query_user.save()
        return Response({'message': 'id is active now'})

class CountryCodeAPIView(APIView):
    serializer_class = CountryCodeSerializer

    def get(self, *args, **kwargs):
        id =kwargs.get('pk')
        country_obj =Country.objects.get(id=id)
        serializer=CountryCodeSerializer(country_obj, many=False)
        return Response(serializer.data)


class PlatformDashboardAPIView(APIView):

    def get(self, request):
        goals = Goal.objects.all()
        profiles = Profile.objects.all()
        wallet = Wallet.objects.all()
        total_donation = Transaction.objects.count()
        thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)

        total_active_goals = goals.aggregate(
            total_active_goals=Count(
                'id',
                filter=Q(status='ACTIVE')
            ),
        )
        total_completed_goals = goals.aggregate(
            total_completed_goals=Count(
                'id',
                filter=Q(status='COMPLETED')
            ),
        )
        total_donee = profiles.aggregate(
            total_donee=Count(
                'id',
                filter=Q(profile_type='DONEE')
            ),
        )
        total_ngo = profiles.aggregate(
            total_ngo=Count(
                'id',
                filter=Q(profile_type='NGO')
            ),
        )

        total_collected = wallet.aggregate(
            total_collected=Sum(
                'amount',
                filter=Q(type='NGO') | Q(type='DONEE')
            ),
        )

        total_raised_in_last_30_days = Transaction.objects.filter(payment_updated_at__gte=thirty_days_ago).aggregate(
            total_raised_in_last_30_days=Sum('paid_amount')
        )

        dashboard_count = {**total_active_goals, **total_completed_goals, **total_donee, **total_ngo, **total_collected,
                     "total_donation": total_donation, **total_raised_in_last_30_days}
        serializer = PlatformDashboardSerializer(dashboard_count, many=False)
        return Response({"dashboard_count": serializer.data})


class PlatformDashboardDoneeAPIView(APIView):

    def get(self, request):
        profiles = Profile.objects.filter(profile_type="DONEE").annotate(
            total_goal = Count('profile_goal'), total_raised = Sum('profile_goal__paid_amount'))
        thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)
        payments = Payment.objects.filter(goal__profile__profile_type="DONEE",
                                      payment_transaction__payment_updated_at__gte=thirty_days_ago).\
            annotate(total_paid_amount=Sum('payment_transaction__paid_amount')).order_by('-total_paid_amount').first()
        if payments:
            goal = Goal.objects.filter(profile=payments.goal.profile).count()
            donee_of_the_month = {"profile": payments.goal.profile, "total_paid_amount": payments.total_paid_amount, "total_goal": goal}
        else:
            donee_of_the_month = {}
        total_donee = profiles.aggregate(
            total_donee=Count(
                'id'
            ),
        )
        total_active_donee = profiles.aggregate(
            total_active_donee=Count(
                'id',
                filter=Q(is_active=True)
            ),
        )
        total_inactive_donee = profiles.aggregate(
            total_inactive_donee=Count(
                'id',
                filter=Q(is_active=False)
            ),
        )

        donee_count = {**total_donee, **total_active_donee, **total_inactive_donee}
        serializer = DashboardDoneeInfoSerializer(donee_count, many=False)
        donee_serializer = DashboardDoneeListSerializer(profiles, many=True)
        donee_of_the_month = DoneeOfTheMonthSerializer(donee_of_the_month, many=False)
        return Response({"donee_count": serializer.data, "donee_list": donee_serializer.data, "donee_of_the_month": donee_of_the_month.data})


class PlatformDashboardDonorAPIView(APIView):

    def get(self, request):
        payments = Payment.objects.filter(status="PAID")
        thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)

        total_donor = payments.aggregate(
            total_donor=Count(
                'user',
                distinct=True
            ),
        )
        total_donation = payments.aggregate(
            total_donation=Count(
                'id',
            ),
        )
        total_raised = payments.aggregate(
            total_raised=Sum(
                'payment_transaction__paid_amount',
            ),
        )
        total_new_donor = payments.aggregate(
            total_new_donor=Count(
                'user',
                filter=Q(payment_transaction__payment_updated_at__gte=thirty_days_ago),
                distinct=True
            ),
        )

        donor_info = {**total_donor, **total_donation, **total_raised, **total_new_donor}
        serializer = PlatformDashboardDonorSerializer(donor_info, many=False)
        return Response({"donor_info": serializer.data})


class PlatformDashboardNGOAPIView(APIView):

    def get(self, request):
        profiles = Profile.objects.filter(profile_type="NGO").annotate(
            total_goal = Count('profile_goal'), total_raised = Sum('profile_goal__paid_amount'))
        # thirty_days_ago = datetime.date.today() - datetime.timedelta(days=90)
        # payments = Payment.objects.filter(goal__profile__profile_type="DONEE",
        #                               payment_transaction__payment_updated_at__gte=thirty_days_ago).\
        #     annotate(total_paid_amount=Sum('payment_transaction__paid_amount')).order_by('-total_paid_amount').first()
        # print(payments.goal.profile)
        total_ngo = profiles.aggregate(
            total_ngo=Count(
                'id'
            ),
        )
        total_active_ngo = profiles.aggregate(
            total_active_ngo=Count(
                'id',
                filter=Q(is_active=True)
            ),
        )
        total_inactive_ngo = profiles.aggregate(
            total_inactive_ngo=Count(
                'id',
                filter=Q(is_active=False)
            ),
        )

        ngo_count = {**total_ngo, **total_active_ngo, **total_inactive_ngo}
        serializer = DashboardNGOInfoSerializer(ngo_count, many=False)
        ngo_serializer = DashboardDoneeListSerializer(profiles, many=True)
        return Response({"ngo_info": serializer.data, "ngo_list": ngo_serializer.data})


class PlatformDashboardWalletAPIView(APIView):

    def get(self, request):
        wallet = Wallet.objects.all()
        # thirty_days_ago = datetime.date.today() - datetime.timedelta(days=90)
        # payments = Payment.objects.filter(goal__profile__profile_type="DONEE",
        #                               payment_transaction__payment_updated_at__gte=thirty_days_ago).\
        #     annotate(total_paid_amount=Sum('payment_transaction__paid_amount')).order_by('-total_paid_amount').first()
        # print(payments.goal.profile)
        total_ngo_income = wallet.aggregate(
            total_ngo_income=Sum(
                'amount',
                filter=Q(type="NGO")
            ),
        )

        total_donee_income = wallet.aggregate(
            total_donee_income=Sum(
                'amount',
                filter=Q(type="DONEE")
            ),
        )

        total_pgw_income = wallet.aggregate(
            total_pgw_income=Sum(
                'amount',
                filter=Q(type="PGW")
            ),
        )

        total_platform_income = wallet.aggregate(
            total_platform_income=Sum(
                'amount',
                filter=Q(type="PLATFORM")
            ),
        )

        wallet_info = {**total_ngo_income, **total_donee_income, **total_pgw_income, **total_platform_income}
        serializer = PlatformDashboardWalletInfoSerializer(wallet_info, many=False)
        return Response({"wallet_info": serializer.data})



    