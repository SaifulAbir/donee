from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import *
from .utils import paypal_token, payment


class DedicationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DedicationInfo
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    is_dedicated = serializers.BooleanField(write_only=True)
    dedicated_message = serializers.CharField(write_only=True, required=False)
    is_gift_dedicated = serializers.BooleanField(write_only=True)
    dedicated_gift_message = serializers.CharField(write_only=True, required=False)
    payment_dedication = DedicationInfoSerializer(many=True, read_only=True)
    class Meta:
        model = Payment
        fields = ('id', 'amount', 'goal', 'status', 'is_dedicated', 'dedicated_message', 'is_gift_dedicated',
                  'dedicated_gift_message', 'payment_dedication')
        read_only_fields = ('status', )

    def create(self, validated_data):
        is_dedicated = validated_data.pop('is_dedicated')
        try:
            dedicated_message = validated_data.pop('dedicated_message')
        except KeyError:
            dedicated_message = None
        is_gift_dedicated = validated_data.pop('is_gift_dedicated')
        try:
            dedicated_gift_message = validated_data.pop('dedicated_gift_message')
        except KeyError:
            dedicated_gift_message = None
        payment_instance = Payment.objects.create(**validated_data, user=self.context['request'].user,
                                                  created_by=self.context['request'].user.id)
        if is_dedicated:
            DedicationInfo.objects.create(type="DEDICATED", payment=payment_instance, is_dedicated=True,
                                          message=dedicated_message, created_by=self.context['request'].user.id)
        if is_gift_dedicated:
            DedicationInfo.objects.create(type="GIFT", payment=payment_instance, is_dedicated=True,
                                          message=dedicated_gift_message, created_by=self.context['request'].user.id)
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

        if payment_status != "COMPLETED":
            raise ValidationError('Payment is not completed yet.')

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

        # Distribution Start
        pgw_amount = round((goal_obj.first().pgw_percentage * float(paid_amount)) / 100, 2)
        platform_amount = round((goal_obj.first().platform_percentage * float(paid_amount)) / 100, 2)
        if goal_obj.first().profile.profile_type == "DONEE":
            ngo_amount = round((goal_obj.first().ngo_percentage * float(paid_amount)) / 100, 2)
            donee_amount = float(paid_amount) - (pgw_amount + platform_amount + ngo_amount)
        else:
            ngo_amount = float(paid_amount) - (pgw_amount + platform_amount)
            donee_amount = None

        distribution = Distribution.objects.create(total_paid_amount=paid_amount, pgw_amount=pgw_amount, platform_amount=platform_amount,
                                    transaction=transaction_instance, ngo_amount=ngo_amount, donee_amount=donee_amount,
                                    created_by = self.context['request'].user.id)
        # Distribution End

        # Platform Wallet Start
        platform_wallet = Wallet.objects.filter(type="PLATFORM")
        if platform_wallet.exists():
            total_platform_amount = platform_amount + platform_wallet.first().amount
            platform_wallet.update(amount = total_platform_amount)
        else:
            platform_wallet = Wallet.objects.create(amount=platform_amount, type="PLATFORM", created_by = self.context['request'].user.id)
        # Platform Wallet End

        # PGW Wallet Start
        pgw_wallet = Wallet.objects.filter(type="PGW")
        if pgw_wallet.exists():
            total_pgw_amount = pgw_amount + pgw_wallet.first().amount
            pgw_wallet.update(amount=total_pgw_amount)
        else:
            pgw_wallet = Wallet.objects.create(amount=pgw_amount, type="PGW", created_by = self.context['request'].user.id)
        # PGW Wallet End

        if goal_obj.first().profile.profile_type == "NGO":
            ngo_wallet = Wallet.objects.filter(type="NGO", profile=goal_obj.first().profile)
            if ngo_wallet.exists():
                total_ngo_amount = ngo_amount + ngo_wallet.first().amount
                ngo_wallet.update(amount=total_ngo_amount)
            else:
                ngo_wallet = Wallet.objects.create(amount=ngo_amount, type="NGO", profile=goal_obj.first().profile,
                                      created_by = self.context['request'].user.id)
        else:
            ngo_wallet = Wallet.objects.filter(type="NGO", profile=goal_obj.first().profile.ngo_profile_id)
            if ngo_wallet.exists():
                total_ngo_amount = ngo_amount + ngo_wallet.first().amount
                ngo_wallet.update(amount=total_ngo_amount)
            else:
                ngo_wallet = Wallet.objects.create(amount=ngo_amount, type="NGO", profile=goal_obj.first().profile.ngo_profile_id,
                                      created_by = self.context['request'].user.id)

            donee_wallet = Wallet.objects.filter(type="DONEE", profile=goal_obj.first().profile)
            if donee_wallet.exists():
                total_donee_amount = donee_amount + donee_wallet.first().amount
                donee_wallet.update(amount=total_donee_amount)
            else:
                donee_wallet = Wallet.objects.create(amount=donee_amount, type="DONEE", profile=goal_obj.first().profile,
                                      created_by = self.context['request'].user.id)

        WalletDistribution.objects.create(distribution=distribution, wallet=platform_wallet,
                                          created_by = self.context['request'].user.id)
        WalletDistribution.objects.create(distribution=distribution, wallet=pgw_wallet,
                                          created_by = self.context['request'].user.id)
        WalletDistribution.objects.create(distribution=distribution, wallet=ngo_wallet,
                                          created_by = self.context['request'].user.id)
        if goal_obj.first().profile.profile_type == "DONEE":
            WalletDistribution.objects.create(distribution=distribution, wallet=donee_wallet,
                                              created_by = self.context['request'].user.id)
        goal_paid_amount = goal_obj.first().paid_amount
        if goal_paid_amount:
            paid_amount = goal_paid_amount + float(paid_amount)
        goal_obj.update(paid_amount=paid_amount)
        return transaction_instance