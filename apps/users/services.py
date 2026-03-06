from rest_framework_simplejwt.tokens import AccessToken
from .models import User


def register_user(validated_data):
    user = User.objects.create_user(**validated_data)
    return user, _generate_token(user)


def get_token(user):
    return _generate_token(user)


def _generate_token(user):
    return str(AccessToken.for_user(user))
