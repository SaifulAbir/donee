import decimal
from warnings import catch_warnings

from django.db.models import Sum, DecimalField, Q
from django.db.models.fields import CharField
from django.db.models.functions import Coalesce
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

        # Total donation by user
        user = User.objects.filter(id=self.context['request'].user.id)
        previous_donated_amount = user.first().total_donated_amount
        total_donated_amount = decimal.Decimal(paid_amount)
        if previous_donated_amount:
            total_donated_amount = previous_donated_amount + decimal.Decimal(paid_amount)
        user.update(total_donated_amount=total_donated_amount)


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
            total_platform_amount = decimal.Decimal(platform_amount) + platform_wallet.first().amount
            platform_wallet.update(amount = total_platform_amount)
            platform_wallet = platform_wallet.first()
        else:
            platform_wallet = Wallet.objects.create(amount=platform_amount, type="PLATFORM", created_by = self.context['request'].user.id)
        # Platform Wallet End

        # PGW Wallet Start
        pgw_wallet = Wallet.objects.filter(type="PGW")
        if pgw_wallet.exists():
            total_pgw_amount = decimal.Decimal(pgw_amount) + pgw_wallet.first().amount
            pgw_wallet.update(amount=total_pgw_amount)
            pgw_wallet = pgw_wallet.first()
        else:
            pgw_wallet = Wallet.objects.create(amount=pgw_amount, type="PGW", created_by = self.context['request'].user.id)
        # PGW Wallet End

        if goal_obj.first().profile.profile_type == "NGO":
            ngo_wallet = Wallet.objects.filter(type="NGO", profile=goal_obj.first().profile)
            if ngo_wallet.exists():
                total_ngo_amount = decimal.Decimal(ngo_amount) + ngo_wallet.first().amount
                ngo_wallet.update(amount=total_ngo_amount)
                ngo_wallet = ngo_wallet.first()
            else:
                ngo_wallet = Wallet.objects.create(amount=ngo_amount, type="NGO", profile=goal_obj.first().profile,
                                      created_by = self.context['request'].user.id)
        else:
            ngo_profile = Profile.objects.get(id = goal_obj.first().profile.ngo_profile_id)
            ngo_wallet = Wallet.objects.filter(type="NGO", profile=ngo_profile)
            if ngo_wallet.exists():
                total_ngo_amount = decimal.Decimal(ngo_amount) + ngo_wallet.first().amount
                ngo_wallet.update(amount=total_ngo_amount)
                ngo_wallet = ngo_wallet.first()
            else:
                ngo_wallet = Wallet.objects.create(amount=ngo_amount, type="NGO", profile=ngo_profile,
                                      created_by = self.context['request'].user.id)

            donee_wallet = Wallet.objects.filter(type="DONEE", profile=goal_obj.first().profile)
            if donee_wallet.exists():
                total_donee_amount = decimal.Decimal(donee_amount) + donee_wallet.first().amount
                donee_wallet.update(amount=total_donee_amount)
                donee_wallet = donee_wallet.first()
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
            paid_amount = goal_paid_amount + decimal.Decimal(paid_amount)
        goal_obj.update(paid_amount=paid_amount)
        if goal_obj.first().paid_amount == goal_obj.first().total_amount:
            goal_obj.update(status="COMPLETED")
        return transaction_instance


class CashoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cashout
        fields = ('remark', "goal", "user", "profile", "status", "requested_amount")
        read_only_fields = ('user', "status", 'requested_amount')

    def create(self, validated_data):
        profile = validated_data["profile"]
        try:
            goal = validated_data["goal"]
        except KeyError as e:
            goal = None
        if goal==None:
            amount = Distribution.objects.filter(
                Q(transaction__payment__goal__profile__ngo_profile_id=profile.id) & Q(ngo_cashout_status="INITIAL")).aggregate(
                    available_amount=Coalesce(Sum(
                        'ngo_amount',
                    ), 0, output_field=DecimalField()),
                )
            distribution = Distribution.objects.filter(
                Q(transaction__payment__goal__profile__ngo_profile_id=profile.id) & Q(ngo_cashout_status="INITIAL"))
            distribution.update(ngo_cashout_status="PENDING")
            cashout_instance = Cashout.objects.create(**validated_data, user=self.context['request'].user,
                                                      requested_amount=amount["available_amount"],
                                                      created_by=self.context['request'].user)
            for each_distribution in distribution:
                CashoutDistribution.objects.create(distribution=each_distribution, cashout=cashout_instance,
                                                   status="PENDING", created_by=self.context['request'].user)
        else:
            if profile.profile_type=="DONEE":
                amount = Distribution.objects.filter(Q(transaction__payment__goal=goal) & Q(donee_cashout_status="INITIAL")).aggregate(
                    available_amount=Coalesce(Sum(
                        'donee_amount',
                    ), 0, output_field=DecimalField()),
                )
                distribution = Distribution.objects.filter(
                    Q(transaction__payment__goal=goal) & Q(donee_cashout_status="INITIAL"))
                distribution.update(donee_cashout_status="PENDING")
                cashout_instance = Cashout.objects.create(**validated_data, user=self.context['request'].user,
                                                          requested_amount=amount["available_amount"],
                                                          created_by=self.context['request'].user)
                for each_distribution in distribution:
                    CashoutDistribution.objects.create(distribution=each_distribution, cashout=cashout_instance,
                                                       status="PENDING", created_by=self.context['request'].user)
            elif profile.profile_type=="NGO":
                amount = Distribution.objects.filter(Q(transaction__payment__goal=goal) & Q(ngo_cashout_status="INITIAL")).aggregate(
                    available_amount=Coalesce(Sum(
                        'ngo_amount',
                    ), 0, output_field=DecimalField()),
                )
                distribution = Distribution.objects.filter(
                    Q(transaction__payment__goal=goal) & Q(ngo_cashout_status="INITIAL"))
                distribution.update(ngo_cashout_status="PENDING")
                cashout_instance = Cashout.objects.create(**validated_data, user=self.context['request'].user,
                                                          requested_amount=amount["available_amount"],
                                                          created_by=self.context['request'].user)
                for each_distribution in distribution:
                    CashoutDistribution.objects.create(distribution=each_distribution, cashout=cashout_instance,
                                                       status="PENDING", created_by=self.context['request'].user)
        return cashout_instance

class CashoutGoalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Goal
        fields = ('id', 'title', 'image', 'slug' )

class CashoutProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('id', 'username', 'profile_type', 'image')


class CashoutHistoryListSerializers(serializers.ModelSerializer):
    goal = CashoutGoalSerializer()
    class Meta:
        model = Cashout
        fields = ('goal', 'requested_amount', 'remark', 'status')

class WaitingforAdminListSerializer(serializers.ModelSerializer):
    goal = CashoutGoalSerializer()
    profile = CashoutProfileSerializer()

    class Meta:
        model = Cashout
        fields = ('id', 'goal', 'profile', 'requested_amount', 'remark', 'status')

class WaitingforNGOListSerializer(serializers.ModelSerializer):
    goal = CashoutGoalSerializer()
    profile = CashoutProfileSerializer()

    class Meta:
        model = Cashout
        fields = ('id', 'goal', 'profile', 'requested_amount', 'remark', 'status')

class CashoutUserUpdateSerializer(serializers.ModelSerializer):
    remark = serializers.CharField(write_only=True, required= False)
    class Meta:
        model=Cashout
        fields=('id', 'status', 'remark')
    
    def update(self, instance, validated_data):
        try:
            remark = validated_data.pop('remark')
        except:
            remark = None

        if validated_data['status'] == "REJECTED_BY_NGO":
            validated_data.update({"ngo_remark" : remark })
        elif validated_data['status'] == "REJECTED_BY_ADMIN":
            validated_data.update({"admin_remark" : remark })
    
        return super().update(instance, validated_data)

            
class CashoutPaidGoalSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all(), many=False)

    class Meta:
        model = Profile
        fields = '__all__'


class CashoutAccountInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashoutAccountInfo
        fields = '__all__'

    def create(self,validated_data,*args,**kwargs):
        profile1 = Profile.objects.get(id=validated_data['profile'].id)
        cashout_account_info = CashoutAccountInfo.objects.create(**validated_data,
                                    created_by=self.context['request'].user.id)

        return cashout_account_info

class CashoutAccountListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CashoutAccountInfo
        fields = ('id', 'profile', 'name', 'type', 'account_number')


class CashoutAccountUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CashoutAccountInfo
        fields = '__all__'


    def update(self, instance, validated_data):
        
        if validated_data['name']:
            validated_data.update({"name" : validated_data['name'] })
        elif validated_data['type']:
            validated_data.update({"type" : validated_data['type'] })
        elif validated_data['account_number']:
            validated_data.update({"account_number" : validated_data['account_number'] })
    
        return super().update(instance, validated_data)



    
