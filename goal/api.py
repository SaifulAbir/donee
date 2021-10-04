from rest_framework.generics import ListAPIView
from goal.models import SDGS
from goal.serializers import SDGSSerializer


class SDGSListAPI(ListAPIView):
    queryset = SDGS.objects.filter()
    serializer_class = SDGSSerializer