from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from common.response import success
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from . import services


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = services.register_user(serializer.validated_data)
        return success(
            data={'user': UserSerializer(user).data, 'accessToken': token},
            message='Account created successfully.',
            status_code=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = services.get_token(user)
        return success(
            data={'user': UserSerializer(user).data, 'accessToken': token},
            message='Login successful.',
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success(data=UserSerializer(request.user).data)
