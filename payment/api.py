from django.conf import settings
from django.template.loader import render_to_string
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import  CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from goal.serializers import PaidGoalSerializer
from .serializers import *
from rest_framework.response import Response
from django.core.mail import EmailMessage, send_mail


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
        profile= self.request.GET.get('profile')
        account_list = CashoutAccountInfo.objects.filter(profile=profile)
        if account_list:
            return account_list
        else:
            raise ValidationError({"Account_info":'there is no account information'})

class CashoutAccountUpdateAPIView(UpdateAPIView):
    serializer_class = CashoutAccountUpdateSerializer
    queryset = CashoutAccountInfo.objects.all()


class DedicationInfoAPIView(APIView):
    @swagger_auto_schema(request_body=DedicationInfoSerializer)
    def post(self, request, *args, **kwargs):
        dedication_serializer = DedicationInfoSerializer(data=request.data)
        if dedication_serializer.is_valid():
            profile = Profile.objects.get(user=self.request.user)
            email_list = request.POST.getlist('emails')
            subject = "A goal have been dedicated to you"
            html_message = render_to_string('dedication_info.html', {'dedicator_username': profile.username})
            send_mail(
                subject=subject,
                message = None,
                from_email=profile.email,
                recipient_list=email_list,
                html_message=html_message
            )
            return Response({'message': 'Email sent successfully!'})
        return Response({'message': dedication_serializer.errors})



       



    

