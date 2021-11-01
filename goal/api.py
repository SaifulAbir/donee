from itertools import chain
from django.db.models import Q, Count, Value, F, CharField, Prefetch, Subquery, Max, Min, ExpressionWrapper, \
    IntegerField
from django.db.models.functions import Concat
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from Donee.pagination import CustomPagination
from Donee.settings import MEDIA_URL
from goal.serializers import PopularGoalSerializer, SearchSerializer
from goal.models import SDGS, Goal, GoalSDGS, Like, Comment
from payment.models import Payment
from goal.models import SDGS, Goal, GoalSDGS, GoalSave,Like,Comment
from user.models import User, Profile
from goal.serializers import GoalCommentSerializer, GoalLikeSerializer, GoalSaveSerializer, SDGSSerializer, GoalSerializer, GoalListSerializer, SingleCatagorySerializer
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
        query = Goal.objects.filter(status='PUBLISHED').annotate(
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
    queryset = Goal.objects.filter(status='PUBLISHED').prefetch_related(
        Prefetch("goal_payment", queryset=Payment.objects.filter(status="PAID").distinct())).order_by('-created_at')
    serializer_class = GoalListSerializer
    pagination_class = CustomPagination


class SingleCatagoryView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SingleCatagorySerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        geturl = self.kwargs['id']
        return GoalSDGS.objects.filter(sdgs__id=geturl,goal__status='PUBLISHED')


class PopularGoalAPI(ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Goal.objects.annotate(
        payment_count=Count(
            Concat('goal_payment__goal', 'goal_payment__user'),
            filter=Q(goal_payment__status='PAID'),
            distinct=True
        )
    ).filter(status='PUBLISHED').order_by('-payment_count')[:5]
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
                values("title", "img", uid=F("slug")).annotate(type = Value("goal"))

            profiles = Profile.objects.filter(full_name__icontains=query). \
                annotate(img=Concat(Value(MEDIA_URL), 'image', output_field=CharField())). \
                values("img", uid=F("id"), title=F("full_name")).annotate(type = Value("profile"))

            users = User.objects.filter(full_name__icontains=query). \
                annotate(img=Concat(Value(MEDIA_URL), 'image', output_field=CharField())). \
                values("img", uid=F("id"), title=F("full_name")).annotate(type = Value("user"))

            search_result = list(chain(goals, profiles, users))
        else:
            search_result = []
        serializer = SearchSerializer(search_result, many=True)
        return Response({"search_result": serializer.data})


class GoalLikeAPI(CreateAPIView):
    serializer_class = GoalLikeSerializer
    queryset = Like.objects.all()

    def create(self, request, *args, **kwargs):
        if self.request.data =={} :
            raise ValidationError({"error":'must provide a goal id!'})
        else:
            if isinstance(self.request.data['goal'], int):
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
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"goal":self.request.data["goal"],"is_like":False,}, status=status.HTTP_200_OK)
                if check_like.exists() and check_like.first().is_like == False:
                    obj = check_like.first()
                    obj.is_like = True
                    obj.save()
                    goal_obj = goal
                    goal_obj.total_like_count +=1
                    goal_obj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"goal":self.request.data["goal"],"is_like":True,}, status=status.HTTP_200_OK)
                else:
                    if check_profile.exists():
                        profile_obj = check_profile.first()
                        goal_obj = goal
                        goal_obj.total_like_count +=1
                        goal_obj.save()
                        likeobj =  Like(user = user,goal = goal,is_like = True,created_by =user.username,has_profile=profile_obj)
                        likeobj.save()
                        return Response({"id":self.request.user.id,"username":self.request.user.username,"goal":self.request.data["goal"],"is_like":True,}, status=status.HTTP_201_CREATED)
                    else:
                        goal_obj = goal
                        goal_obj.total_like_count +=1
                        goal_obj.save()
                        likeobj= Like(user = user,goal = goal,is_like = True,created_by =user.username)
                        likeobj.save()
                        return Response({"id":self.request.user.id,"username":self.request.user.username,"goal":self.request.data["goal"],"is_like":True,}, status=status.HTTP_201_CREATED)
                # return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                raise ValidationError({"error":'must provide integer goal id!'})
    



class GoalCommentAPI(CreateAPIView):
    serializer_class = GoalCommentSerializer
    queryset = Comment.objects.all()

    def create(self, request, *args, **kwargs):
        if self.request.data =={} :
            raise ValidationError({"error":'must provide a goal id!'})
        else:
            if isinstance(self.request.data['goal'], int) and 'text' in self.request.data:
                user = User.objects.get(id = self.request.user.id)
                try:
                    goal = Goal.objects.get(id = self.request.data['goal'])
                    check_profile = Profile.objects.filter(user = self.request.user.id)
                    if check_profile.exists():
                        profile_obj = check_profile.first()
                        comment_obj = Comment(user = user,goal = goal,created_by =user.username,text=self.request.data['text'],has_profile =profile_obj)
                        comment_obj.save()
                        goal_obj = goal
                        goal_obj.total_comment_count +=1
                        goal_obj.save()
                        return Response({"id":self.request.user.id,"username":self.request.user.username,"goal":self.request.data["goal"],"text":self.request.data["text"]}, status=status.HTTP_201_CREATED)
                    else:
                        comment_obj = Comment(user = user,goal = goal,text=self.request.data['text'],created_by =user.username)
                        comment_obj.save()
                        goal_obj = goal
                        goal_obj.total_comment_count +=1
                        goal_obj.save()
                        return Response({"id":self.request.user.id,"username":self.request.user.username,"goal":self.request.data["goal"],"text":self.request.data["text"]}, status=status.HTTP_201_CREATED)
                except Goal.DoesNotExist:
                     raise ValidationError({"error":"goal not exist!"})
            else:
                raise ValidationError({"error":'must provide integer goal id and text .'})




class GoalSaveAPI(CreateAPIView):
    serializer_class = GoalSaveSerializer
    queryset = GoalSave.objects.all()

    def create(self, request, *args, **kwargs):
        if self.request.data =={} :
            raise ValidationError({"error":'must provide a goal id!'})
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
                    savedobj =  GoalSave(user = user,goal = goal,is_saved = True,created_by =user.username,has_profile=profile_obj)
                    savedobj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"goal":self.request.data["goal"],"is_saved":True,}, status=status.HTTP_201_CREATED)
                else:
                    savedobj= GoalSave(user = user,goal = goal,is_saved = True,created_by =user.username)
                    savedobj.save()
                    return Response({"id":self.request.user.id,"username":self.request.user.username,"goal":self.request.data["goal"],"is_saved":True,}, status=status.HTTP_201_CREATED)
        
    

