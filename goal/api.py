from itertools import chain

from django.db.models import FilteredRelation, Q, Count, Value, F, CharField
from django.db.models.functions import Concat
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from Donee.pagination import CustomPagination
from Donee.settings import MEDIA_URL
from goal.models import SDGS, Goal, GoalSDGS
from goal.serializers import SDGSSerializer, GoalSerializer, GoalListSerializer, SingleCatagorySerializer, \
    PopularGoalSerializer, SearchSerializer
from user.models import Profile, User


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


class PopularGoalAPI(ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Goal.objects.annotate(
        payment = FilteredRelation(
            'goal_payment', condition=Q(goal_payment__status='PAID')
        )
    ).annotate(
        payment_count=Count('payment')
    ).filter(status='PUBLISHED').order_by('-payment_count')[:5]
    serializer_class = PopularGoalSerializer


class SearchAPIView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        query = request.GET.get('query')
        if query:
            goals = Goal.objects.filter(title=query).\
                annotate(img=Concat(Value(MEDIA_URL), 'image', output_field=CharField())).\
                values("title", "img", uid=F("slug")).annotate(type = Value("goal"))

            profiles = Profile.objects.filter(full_name=query).\
                annotate(img=Concat(Value(MEDIA_URL), 'image', output_field=CharField())).\
                values("img", uid=F("id"), title=F("full_name")).annotate(type = Value("profile"))

            users = User.objects.filter(full_name=query).\
                annotate(img=Concat(Value(MEDIA_URL), 'image', output_field=CharField())).\
                values("img", uid=F("id"), title=F("full_name")).annotate(type = Value("user"))

            search_result = list(chain(goals, profiles, users))
        else:
            search_result = []
        serializer = SearchSerializer(search_result, many=True)
        return Response({"search_result": serializer.data})