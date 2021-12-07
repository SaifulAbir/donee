from itertools import chain
from django.db.models import Q, Count, Value, F, CharField, Prefetch, Subquery, Max, Min, ExpressionWrapper, \
    IntegerField, Sum, DecimalField
from django.db.models.functions import Concat, text, Coalesce
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from Donee.pagination import CustomPagination
from Donee.settings import MEDIA_URL
from goal.serializers import GoalCommentCreateSerializer, PopularGoalSerializer, SearchSerializer, \
    DashboardGoalCountSerializer, DashboardGoalListSerializer, PaidGoalListSerializer, PaidGoalSerializer
from goal.models import SDGS, Goal, GoalSDGS, Like, Comment, Setting
from notification.models import LiveNotification
from payment.models import Payment
from goal.models import SDGS, Goal, GoalSDGS, GoalSave,Like,Comment
from user.models import User, Profile
from goal.serializers import GoalCommentSerializer, GoalLikeSerializer, GoalSaveSerializer, SDGSSerializer, \
     GoalSerializer, GoalListSerializer, SingleCatagorySerializer, GetPercentagesSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError



class SDGSListAPI(ListAPIView):
    permission_classes = (AllowAny,)
    queryset = SDGS.objects.filter(status=True)
    serializer_class = SDGSSerializer


class GoalCreateAPIView(CreateAPIView):
    serializer_class = GoalSerializer

    def post(self, request, *args, **kwargs):
        return super(GoalCreateAPIView, self).post(request, *args, **kwargs)


class GoalRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = GoalSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = "slug"

    def get_queryset(self):
        slug = self.kwargs['slug']
        payment = Payment.objects.filter(goal=Goal.objects.get(slug=slug), status="PAID").order_by('user', '-created_at').distinct('user')
        query = Goal.objects.annotate(
            donor_count=Count(
                Concat('goal_payment__goal', 'goal_payment__user'),
                filter=Q(goal_payment__status='PAID'),
                distinct=True
            ) - 1
        ).prefetch_related(
        Prefetch("goal_payment", queryset=Payment.objects.filter(id__in=payment).order_by('-created_at')))
        return query

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class GoalListAPI(ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Goal.objects.filter(status='ACTIVE').prefetch_related(
        Prefetch("goal_payment", queryset=Payment.objects.filter(status="PAID").distinct())).order_by('-created_at')
    serializer_class = GoalListSerializer
    pagination_class = CustomPagination


class SingleCatagoryView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SingleCatagorySerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        geturl = self.kwargs['id']
        return GoalSDGS.objects.filter(sdgs__id=geturl,goal__status='ACTIVE')


class PopularGoalAPI(ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Goal.objects.annotate(
        payment_count=Count(
            Concat('goal_payment__goal', 'goal_payment__user'),
            filter=Q(goal_payment__status='PAID'),
            distinct=True
        )
    ).filter(status='ACTIVE').order_by('-payment_count')[:5]
    serializer_class = PopularGoalSerializer


class SupportedGoalAPI(ListAPIView):
    serializer_class = PopularGoalSerializer

    def get_queryset(self):
        queryset = Goal.objects.filter(goal_payment__user=self.request.user, goal_payment__status="PAID").distinct().\
            annotate(percentage = ExpressionWrapper((F('paid_amount')/F("total_amount"))*100, output_field=IntegerField()))
        return queryset


class SearchAPIView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        query = request.GET.get('query')
        if query:
            goals = Goal.objects.filter(title__icontains=query). \
                annotate(img=Concat(Value(MEDIA_URL), 'image', output_field=CharField())). \
                values("title", "img", uid=F("slug")).annotate(type = Value("GOAL"))

            profiles = Profile.objects.filter(full_name__icontains=query). \
                annotate(img=Concat(Value(MEDIA_URL), 'image', output_field=CharField())). \
                values("img", uid=F("id"), title=F("full_name")).annotate(type = F("profile_type"))

            users = User.objects.filter(full_name__icontains=query). \
                annotate(img=Concat(Value(MEDIA_URL), 'image', output_field=CharField())). \
                values("img", uid=F("id"), title=F("full_name")).annotate(type = Value("USER"))

            search_result = list(chain(goals, profiles, users))
        else:
            search_result = []
        serializer = SearchSerializer(search_result, many=True)
        return Response({"search_result": serializer.data})


class GoalLikeAPIView(CreateAPIView):
    serializer_class = GoalLikeSerializer
    queryset = Like.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        
        if self.request.data =={} :
            raise ValidationError({"error":'must provide a goal id!'})
        
        else:
            
                user = User.objects.get(id = self.request.user.id)
                goal = Goal.objects.get(id = self.request.data['goal'])
                check_like = Like.objects.filter(user = self.request.user.id,goal = self.request.data['goal'])
                check_profile = Profile.objects.filter(user = self.request.user.id)
                if check_like.exists() and check_like.first().is_like == True:
                    obj = check_like.first()
                    obj.is_like = False
                    obj.save()
                    goal_obj = goal
                    goal_obj.total_like_count -=1
                    goal_obj.save()

                    # Notification
                    text = '@{} unliked your goal'.format(user.username)
                    LiveNotification.objects.create(text=text, type='GOAL_LIKE',
                                                    from_user=user, to_user=goal_obj.profile.user)
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"goal":self.request.data["goal"],"is_like":False,}, status=status.HTTP_200_OK)
                if check_like.exists() and check_like.first().is_like == False:
                    obj = check_like.first()
                    obj.is_like = True
                    obj.save()
                    goal_obj = goal
                    goal_obj.total_like_count +=1
                    goal_obj.save()

                    # Notification
                    text = '@{} liked your goal'.format(user.username)
                    LiveNotification.objects.create(text=text, type='GOAL_LIKE',
                                                    from_user=user, to_user=goal_obj.profile.user)
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"goal":self.request.data["goal"],"is_like":True,}, status=status.HTTP_200_OK)
                else:
                    if check_profile.exists():
                        profile_obj = check_profile.first()
                        goal_obj = goal
                        goal_obj.total_like_count +=1
                        goal_obj.save()
                        likeobj =  Like(user = user,goal = goal,is_like = True,created_by =user.username)
                        likeobj.save()

                        # Notification
                        text = '@{} liked your goal'.format(user.username)
                        LiveNotification.objects.create(text=text, type='GOAL_LIKE',
                                                        from_user=user, to_user=goal_obj.profile.user)
                        return Response({"id":self.request.user.id,"username":self.request.user.username,"goal":self.request.data["goal"],"is_like":True,}, status=status.HTTP_201_CREATED)
                    else:
                        goal_obj = goal
                        goal_obj.total_like_count +=1
                        goal_obj.save()
                        likeobj= Like(user = user,goal = goal,is_like = True,created_by =user.username)
                        likeobj.save()

                        # Notification
                        text = '@{} liked your goal'.format(user.username)
                        LiveNotification.objects.create(text=text, type='GOAL_LIKE',
                                                        from_user=user, to_user=goal_obj.profile.user)
                        return Response({"id":self.request.user.id,"username":self.request.user.username,"goal":self.request.data["goal"],"is_like":True,}, status=status.HTTP_201_CREATED)
                # return Response(serializer.data, status=status.HTTP_201_CREATED)
            
    



class GoalCreateCommentAPI(CreateAPIView):
    serializer_class = GoalCommentSerializer
    queryset = Comment.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        
        if self.request.data =={} :
            raise ValidationError({"error":'must provide a goal id!'})
        else:
            
                user = User.objects.get(id = self.request.user.id)
                try:
                    goal = Goal.objects.get(id = self.request.data['goal'])
                    check_profile = Profile.objects.filter(user = self.request.user.id)
                    if check_profile.exists():
                        profile_obj = check_profile.first()
                        comment_obj = Comment(user = user,goal = goal,created_by =user.username,text=self.request.data['text'])
                        comment_obj.save()
                        goal_obj = goal
                        goal_obj.total_comment_count +=1
                        goal_obj.save()

                        # Notification
                        text = '@{} commented in your goal'.format(user.username)
                        LiveNotification.objects.create(text=text, type='GOAL_COMMENT',
                                                        from_user=user, to_user=goal_obj.profile.user)
                        return Response({"id":self.request.user.id,"username":self.request.user.username,"goal":self.request.data["goal"],"text":self.request.data["text"]}, status=status.HTTP_201_CREATED)
                    else:
                        comment_obj = Comment(user = user,goal = goal,text=self.request.data['text'],created_by =user.username)
                        comment_obj.save()
                        goal_obj = goal
                        goal_obj.total_comment_count +=1
                        goal_obj.save()

                        # Notification
                        text = '@{} commented in your goal'.format(user.username)
                        LiveNotification.objects.create(text=text, type='GOAL_COMMENT',
                                                        from_user=user, to_user=goal_obj.profile.user)
                        return Response({"id":self.request.user.id,"username":self.request.user.username,"goal":self.request.data["goal"],"text":self.request.data["text"]}, status=status.HTTP_201_CREATED)
                except Goal.DoesNotExist:
                     raise ValidationError({"error":"goal not exist!"})
            




class GoalSaveAPI(CreateAPIView):
    serializer_class = GoalSaveSerializer
    queryset = GoalSave.objects.all()
    
    def create(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True) 
        
        if self.request.data =={}:
            raise ValidationError({"goal":'this field may not be null'
            })
        else:
            user = User.objects.get(id = self.request.user.id)
            goal = Goal.objects.get(id = self.request.data['goal'])
            check_save = GoalSave.objects.filter(user = self.request.user.id,goal = self.request.data['goal'])
            check_profile = Profile.objects.filter(user = self.request.user.id)
            if check_save.exists() and check_save.first().is_saved == True:
                obj = check_save.first()
                obj.is_saved = False
                obj.save()
                return Response({"id":self.request.user.id,"username":self.request.user.username,"goal":self.request.data["goal"],"is_saved":False,}, status=status.HTTP_200_OK)
            if check_save.exists() and check_save.first().is_saved == False:
                obj = check_save.first()
                obj.is_saved = True
                obj.save()
                return Response({"id":self.request.user.id,"username":self.request.user.username,"goal":self.request.data["goal"],"is_saved":True,}, status=status.HTTP_200_OK)
            else:
                if check_profile.exists():
                    profile_obj = check_profile.first()
                    savedobj =  GoalSave(user = user,goal = goal,is_saved = True,created_by =user.username)
                    savedobj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"goal":self.request.data["goal"],"is_saved":True,}, status=status.HTTP_201_CREATED)
                else:
                    savedobj= GoalSave(user = user,goal = goal,is_saved = True,created_by =user.username)
                    savedobj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"goal":self.request.data["goal"],"is_saved":True,}, status=status.HTTP_201_CREATED)


class GoalCommentCreateAPIView(CreateAPIView):
    serializer_class = GoalCommentCreateSerializer


class GoalLikeCreateAPIView(CreateAPIView):
    serializer_class = GoalLikeSerializer


class DashboardGoalCountAPIView(APIView):

    def get(self, request):
        profile = Profile.objects.get(user=self.request.user)
        goals = Goal.objects.filter(Q(profile=profile) | Q(profile__ngo_profile_id = profile.id))
        active_goals = goals.aggregate(
            active_goals=Count(
                'id',
                filter=Q(status='ACTIVE')
            ),
        )
        completed_goals = goals.aggregate(
            completed_goals=Count(
                'id',
                filter=Q(status='COMPLETED')
            ),
        )
        pending_goals = goals.aggregate(
            pending_goals=Count(
                'id',
                filter=Q(status='PENDING')
            ),
        )
        rejected_goals = goals.aggregate(
            rejected_goals=Count(
                'id',
                filter=Q(status='REJECTED')
            ),
        )

        try:
            average_goal_conversion_rate = (completed_goals["completed_goals"]/(active_goals["active_goals"]+completed_goals["completed_goals"]))*100
        except ZeroDivisionError:
            average_goal_conversion_rate = 0

        goal_count = {**active_goals, **completed_goals, **pending_goals, **rejected_goals, "average_goal_conversion_rate": average_goal_conversion_rate}
        serializer = DashboardGoalCountSerializer(goal_count, many=False)
        return Response({"goal_count": serializer.data})


class DashboardGoalListAPIView(ListAPIView):
    serializer_class = DashboardGoalListSerializer

    def get_queryset(self):
        profile = Profile.objects.get(user=self.request.user)
        return Goal.objects.filter(Q(profile=profile) | Q(profile__ngo_profile_id = profile.id))


class GoalStatusUpdateAPI(CreateAPIView):
    serializer_class = GoalSerializer
    queryset = Goal.objects.all()
    
    def create(self, request, *args, **kwargs):
        
       
        
        if self.request.data =={}:
            raise ValidationError({"goal":'this field may not be null'
            })
        else:
            goal = Goal.objects.get(id = self.request.data['goal'])
            status = self.request.data['status']
            
            if goal:
                obj = goal
                obj.status = status
                obj.save()
                return Response({"id":self.request.data['goal'],"status":self.request.data["status"]})
            
            else:
                raise ValidationError({"goal":'this field may not be null'
            })


class PaidGoalListAPIView(APIView):
    @swagger_auto_schema(request_body=PaidGoalSerializer)
    def post(self, request):
        paid_goal_serializer = PaidGoalSerializer(data=request.data)
        if paid_goal_serializer.is_valid():
            profile = Profile.objects.get(id=request.POST.get("profile"))
            # profile = Profile.objects.get(user=self.request.user)
            if profile.profile_type=="DONEE":
                goals = Goal.objects.filter(Q(profile=profile)).annotate(
                    available_amount=Coalesce(Sum(
                        'goal_payment__payment_transaction__transaction_distribution__donee_amount',
                        filter=Q(goal_payment__status='PAID') & ~Q(goal_payment__payment_transaction__transaction_distribution__donee_cashout_status="PENDING")
                    ), 0, output_field=DecimalField())
                )
            elif profile.profile_type=="NGO":
                goals = Goal.objects.filter(Q(profile=profile)).annotate(
                    available_amount=Coalesce(Sum(
                        'goal_payment__payment_transaction__transaction_distribution__ngo_amount',
                        filter=Q(goal_payment__status='PAID') & ~Q(goal_payment__payment_transaction__transaction_distribution__ngo_cashout_status="PENDING")
                    ), 0, output_field=DecimalField())
                )
            donee_goals = Goal.objects.filter(Q(profile__ngo_profile_id = profile.id))

            ngo_amount_from_donee = donee_goals.aggregate(
                available_amount=Coalesce(Sum(
                    'goal_payment__payment_transaction__transaction_distribution__ngo_amount',
                    filter=Q(goal_payment__status='PAID') & ~Q(
                        goal_payment__payment_transaction__transaction_distribution__ngo_cashout_status="PENDING")
                ), 0, output_field=DecimalField()),
            )

            ngo_amount_from_donee = {"ngo_amount_from_donee": ngo_amount_from_donee["available_amount"]}
            goal_list = PaidGoalListSerializer(goals, many=True).data
            data = {"goals": goal_list}
            if profile.profile_type=="NGO":
                data = {"goals": goal_list, "ngo_amount_from_donee": ngo_amount_from_donee}
            return Response(data)

class GetPercentagesAPIView(ListAPIView):
    serializer_class = GetPercentagesSerializer
    
    def get_queryset(self):
        percentages = Setting.objects.all()
        if percentages:
            return percentages
        else:
            raise ValidationError({"percentages":'there is no percentage'})


    

    

   