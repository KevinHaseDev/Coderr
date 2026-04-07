from django.contrib.auth import get_user_model
from rest_framework import serializers

from profiles_app.models import Profile

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    repeated_password = serializers.CharField(write_only=True, min_length=8)
    type = serializers.ChoiceField(
        choices=[Profile.TYPE_CUSTOMER, Profile.TYPE_BUSINESS])

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username is already in use.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email is already in use.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {'repeated_password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        user_type = validated_data.pop('type')
        validated_data.pop('repeated_password')
        password = validated_data.pop('password')

        user = User.objects.create_user(password=password, **validated_data)
        Profile.objects.create(user=user, type=user_type)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
