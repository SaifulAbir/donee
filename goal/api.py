from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny
from Donee.pagination import CustomPagination
from goal.models import SDGS, Goal, GoalSDGS,Like,Comment
from user.models import User, Profile
from goal.serializers import GoalCommentSerializer, GoalLikeSerializer, SDGSSerializer, GoalSerializer, GoalListSerializer, SingleCatagorySerializer
from rest_framework.response import Response
from rest_framework import status

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
        return Goal.objects.filter(status='PUBLISHED')

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class GoalListAPI(ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Goal.objects.filter(status='PUBLISHED').order_by('-created_at')
    serializer_class = GoalListSerializer
    pagination_class = CustomPagination


class SingleCatagoryView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SingleCatagorySerializer
    pagination_class = CustomPagination

    def get_queryset(self):
         geturl = self.kwargs['id']
         return GoalSDGS.objects.filter(sdgs__id=geturl,goal__status='PUBLISHED')



class GoalLikeAPI(CreateAPIView):
    serializer_class = GoalLikeSerializer
    queryset = Like.objects.all()

    def perform_create(self, serializer):
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
            return Response(serializer.data, status=status.HTTP_200_OK)
        if check_like.exists() and check_like.first().is_like == False:
            obj = check_like.first()
            obj.is_like = True
            obj.save()
            goal_obj = goal
            goal_obj.total_like_count +=1
            goal_obj.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            if check_profile.exists():
                profile_obj = check_profile.first()
                goal_obj = goal
                goal_obj.total_like_count +=1
                goal_obj.save()
                serializer.save(user = user,goal = goal,is_like = True,created_by =user.username,has_profile=profile_obj)
            else:
                goal_obj = goal
                goal_obj.total_like_count +=1
                goal_obj.save()
                serializer.save(user = user,goal = goal,is_like = True,created_by =user.username)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    



class GoalCommentAPI(CreateAPIView):
    serializer_class = GoalCommentSerializer
    queryset = Comment.objects.all()

    def perform_create(self, serializer):
        user = User.objects.get(id = self.request.user.id)
        goal = Goal.objects.get(id = self.request.data['goal'])
        check_profile = Profile.objects.filter(user = self.request.user.id)
        
        if check_profile.exists():
            profile_obj = check_profile.first()
            serializer.save(user = user,goal = goal,created_by =user.username,has_profile =profile_obj)
            goal_obj = goal
            goal_obj.total_comment_count +=1
            goal_obj.save()
        else:
            serializer.save(user = user,goal = goal,created_by =user.username)
            goal_obj = goal
            goal_obj.total_comment_count +=1
            goal_obj.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)