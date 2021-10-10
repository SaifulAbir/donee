from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateAPIView
from goal.models import SDGS, Goal
from goal.serializers import SDGSSerializer, GoalSerializer, GoalListSerializer


class SDGSListAPI(ListAPIView):
    queryset = SDGS.objects.filter(status=True)
    serializer_class = SDGSSerializer


class GoalCreateAPIView(CreateAPIView):
    serializer_class = GoalSerializer

    def post(self, request, *args, **kwargs):
        return super(GoalCreateAPIView, self).post(request, *args, **kwargs)


class GoalRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = GoalSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = "slug"

    def get_queryset(self):
        return Goal.objects.filter(status='PUBLISHED')

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class GoalListAPI(ListAPIView):
    queryset = Goal.objects.filter(status='PUBLISHED').order_by('-created_at')
    serializer_class = GoalListSerializer