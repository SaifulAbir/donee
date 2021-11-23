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
        profile = Profile.objects.get(id=request.POST.get("profile"))
        queryset = Cashout.objects.filter(profile=profile)
        cashout_history_list = CashoutHistoryListSerializers(queryset, many=True).data  
        return Response(cashout_history_list)
        
        
            
    

class WaitingforAdminListAPIView(ListAPIView):
    queryset = Cashout.objects.all()
    serializer_class = WaitingforAdminListSerializer


class WaitingforNGOListAPIView(APIView):

    def post(self, request):
        profile = Profile.objects.get(id=request.POST.get("profile"))
        donees=Profile.objects.filter(ngo_profile_id=profile.id)
        print(donees)
        list=[]
        for donee in donees: 
            queryset = Cashout.objects.filter(profile=donee, status="PENDING")
            for cash in queryset:
                list.append(cash)
        print(list)
        list = WaitingforNGOListSerializer(queryset, many=True).data  

        return Response(list)
        


class CashoutStatusUpdateAPIView(UpdateAPIView):
    queryset=Cashout.objects.all()
    serializer_class= CashoutUserUpdateSerializer



