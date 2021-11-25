from rest_framework.generics import  CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.serializers import Serializer
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
        print(queryset)
        
        cashout_history_list = CashoutHistoryListSerializers(queryset, many=True).data  
        return Response(cashout_history_list)
        
        
class WaitingforAdminListAPIView(ListAPIView):
    queryset = Cashout.objects.all()
    serializer_class = WaitingforAdminListSerializer


class WaitingforNGOListAPIView(APIView):

    def post(self, request):
        profile = Profile.objects.get(id=request.POST.get("profile"))
        donees=Profile.objects.filter(ngo_profile_id=profile.id)
        list=[]
        for donee in donees: 
            queryset = Cashout.objects.filter(profile=donee, status="PENDING")
            for cash in queryset:
                list.append(cash)
                print(list)
        donee_list = WaitingforNGOListSerializer(list, many=True).data  

        return Response(donee_list)
        


class CashoutStatusUpdateAPIView(UpdateAPIView):
    queryset=Cashout.objects.all()
    serializer_class= CashoutUserUpdateSerializer



class CashoutAccountInfoAPIView(CreateAPIView):
    serializer_class = CashoutAccountInfoSerializer

class CashoutAccountListAPIView(ListAPIView):
    serializer_class = CashoutAccountListSerializer

    def get_queryset(self):
        profile= Profile.objects.get(user=self.request.user)
        account_list = CashoutAccountInfo.objects.filter(profile=profile)
        if account_list:
            return account_list
        else:
            raise ValidationError({"Account_info":'there is no account information'})

class CashoutAccountUpdateAPIView(UpdateAPIView):
    serializer_class = CashoutAccountUpdateSerializer
    queryset = CashoutAccountInfo.objects.all()
       



    

