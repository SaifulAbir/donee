from rest_framework import serializers
from .models import *
from .utils import paypal_token, payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'amount', 'goal', 'status')
        read_only_fields = ('status', )

    def create(self, validated_data):
        payment_instance = Payment.objects.create(**validated_data,user=self.context['request'].user,created_by=self.context['request'].user.id)
        return payment_instance


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('order_id', "payment", 'order_status', "order_updated_at", "payment_created_at", "payer_email",
                  "payment_status", 'paid_amount', 'currency_code')
        read_only_fields = ('order_status', "order_updated_at", "payment_created_at", 'payer_email', 'payment_status',
                            'paid_amount', 'currency_code')

    def create(self, validated_data):
        resp = paypal_token()
        payment_resp = payment(resp["access_token"], validated_data["order_id"])

        order_status = payment_resp["status"]
        payer_email = payment_resp["payer"]["email_address"]
        payer_id = payment_resp["payer"]["payer_id"]
        payer_name = payment_resp["payer"]["name"]["given_name"] + " " + payment_resp["payer"]["name"]["surname"]
        payee_email = payment_resp["purchase_units"][0]["payee"]["email_address"]
        merchant_id = payment_resp["purchase_units"][0]["payee"]["merchant_id"]
        order_updated_at = payment_resp["update_time"]
        pay_id = payment_resp["purchase_units"][0]["payments"]["captures"][0]["id"]
        payment_status = payment_resp["purchase_units"][0]["payments"]["captures"][0]["status"]
        paid_amount = payment_resp["purchase_units"][0]["payments"]["captures"][0]["amount"]["value"]
        currency_code = payment_resp["purchase_units"][0]["payments"]["captures"][0]["amount"]["currency_code"]
        payment_created_at = payment_resp["purchase_units"][0]["payments"]["captures"][0]["create_time"]
        payment_updated_at = payment_resp["purchase_units"][0]["payments"]["captures"][0]["update_time"]

        payment_obj = Payment.objects.filter(id=validated_data["payment"].id)
        goal_obj = Goal.objects.filter(id=payment_obj.first().goal.id)
        transaction_instance = Transaction.objects.create(**validated_data, order_status=order_status,
                                                          payer_email=payer_email, payer_id=payer_id,
                                                          payer_name=payer_name, payee_email=payee_email,
                                                          merchant_id=merchant_id, order_updated_at=order_updated_at,
                                                          pay_id=pay_id, payment_status=payment_status,
                                                          paid_amount=paid_amount, currency_code=currency_code,
                                                          payment_created_at=payment_created_at,
                                                          payment_updated_at=payment_updated_at,
                                                          previous_paid_amount=goal_obj.first().paid_amount,
                                                          created_by=self.context['request'].user.id)
        payment_obj.update(status="PAID")
        goal_paid_amount = goal_obj.first().paid_amount
        if goal_paid_amount:
            paid_amount = goal_paid_amount + paid_amount
        goal_obj.update(paid_amount=paid_amount)
        return transaction_instance