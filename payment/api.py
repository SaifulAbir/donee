from rest_framework.generics import  CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.views import APIView

from goal.serializers import PaidGoalSerializer
from .serializers import *
from rest_framework.response import Response


class PaymentCreateAPIView(CreateAPIView):
    serializer_class = PaymentSerializer


class TransactionCreateAPIView(CreateAPIView):
    serializer_class = TransactionSerializer


class CashoutCreateAPIView(CreateAPIView):
    serializer_class = CashoutSerializer


class CashoutHistoryListAPIView(APIView):
     
     def post(self, request):
        history_goal_serializer = PaidGoalSerializer(data=request.data)
        if history_goal_serializer.is_valid():
            profile = Profile.objects.get(id=request.POST.get("profile"))
            queryset = Cashout.objects.filter(profile=profile)
            cashout_history_list = CashoutHistoryListSerializers(queryset, many=True).data  
            return Response(cashout_history_list)
    

class WaitingforAdminListAPIView(ListAPIView):
    serializer_class = WaitingforAdminListSerializer

class WaitingforNGOListAPIView(APIView):

    def post(self, request):
        ngo_paid_goal_serializer = PaidGoalSerializer(data=request.data)
        if ngo_paid_goal_serializer.is_valid():
            profile = Profile.objects.get(id=request.POST.get("profile"))
            donees=Profile.objects.filter(ngo_profile_id=profile.id)
            queryset = Cashout.objects.filter(profile=donees)
            waiting_for_ngo_list = WaitingforNGOListSerializer(queryset, many=True).data  
            return Response(waiting_for_ngo_list)


class CashoutStatusUpdateAPIView(UpdateAPIView):
    queryset=Cashout.objects.all()
    serializer_class= CashoutUserUpdateSerializer



