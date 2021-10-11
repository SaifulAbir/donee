
from .serializers import *
from rest_framework.generics import   ListAPIView
from .models import *

# from rest_framework.response import Response
# from rest_framework.exceptions import ValidationError
# from rest_framework import status


class SingleCatagoryView(ListAPIView):

    serializer_class = SingleCatagorySerializer

    def get_queryset(self):
         geturl = self.kwargs['title']
         return GoalSDGS.objects.filter(sdgs__title=geturl,goal__status='PUBLISHED')