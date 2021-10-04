from rest_framework.generics import ListAPIView, CreateAPIView
from goal.models import SDGS
from goal.serializers import SDGSSerializer, GoalSerializer


class SDGSListAPI(ListAPIView):
    queryset = SDGS.objects.filter(status=True)
    serializer_class = SDGSSerializer


class GoalCreateAPIView(CreateAPIView):
    serializer_class = GoalSerializer

    def post(self, request, *args, **kwargs):
        return super(GoalCreateAPIView, self).post(request, *args, **kwargs)