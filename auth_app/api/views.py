from django.contrib.auth import authenticate
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from auth_app.api.serializers import LoginSerializer, RegistrationSerializer


def _build_auth_payload(user, token):
    """Return the shared authentication response payload."""
    return {
        'token': token.key,
        'username': user.username,
        'email': user.email,
        'user_id': user.id,
    }


class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response(_build_auth_payload(user, token), status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self._get_authenticated_user(serializer.validated_data)
        if user is None:
            return Response(
                {'detail': 'Invalid credentials.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response(_build_auth_payload(user, token), status=status.HTTP_200_OK)

    def _get_authenticated_user(self, validated_data):
        return authenticate(
            username=validated_data['username'],
            password=validated_data['password'],
        )
