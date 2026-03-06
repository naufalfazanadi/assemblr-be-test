from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator

from common.serializers import StrictMixin
from .models import User


class RegisterSerializer(StrictMixin, serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
                message='Password must contain at least 8 characters, one uppercase, one lowercase, one number and one special character.',
                code='invalid_password',
            )
        ]
    )

    class Meta:
        model = User
        fields = ['email', 'name', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(StrictMixin, serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
                message='Password must contain at least 8 characters, one uppercase, one lowercase, one number and one special character.',
                code='invalid_password',
            )
        ]
    )

    def validate(self, attrs):
        user = authenticate(username=attrs['email'], password=attrs['password'])
        if not user or not user.is_active:
            raise serializers.ValidationError('Invalid credentials.')
        attrs['user'] = user
        return attrs


class UserSerializer(StrictMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'email', 'created_at', 'updated_at']
