from rest_framework import serializers
from .models import *
from rest_framework.validators import UniqueValidator


class UserRegSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'full_name', 'country', 'phone_number', 'bio', 'image']


class DoneeAndNgoProfileCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ('user', 'plan_id', 'view_count', 'is_approved')

    def create(self, validated_data):
        profile_instance = Profile.objects.create(**validated_data, user=self.context['request'].user)
        return profile_instance

    def update(self, instance, validated_data):
        validated_data.update({"user": self.context['request'].user})
        return super().update(instance, validated_data)
        



    
