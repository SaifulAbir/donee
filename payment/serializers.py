from rest_framework import serializers
from .models import *
from .utils import paypal_token, payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('amount','goal')

    
    def create(self, validated_data):
        # resp = paypal_token()
        # print(resp["access_token"])
        # payment_resp = payment(resp["access_token"], validated_data["amount"])
        # print(payment_resp)
        payment_instance = Transaction.objects.create(**validated_data,user=self.context['request'].user,created_by=self.context['request'].user.id)
        return payment_instance