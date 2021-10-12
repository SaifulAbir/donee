from rest_framework import serializers
from .models import *




class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('amount','goal')

    
    def create(self, validated_data):
        payment_instance = Transaction.objects.create(**validated_data,user=self.context['request'].user,created_by=self.context['request'].user.id)
        return payment_instance