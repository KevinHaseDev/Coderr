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
    """View for user registration with profile type selection."""
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """Override to return auth payload with token on successful registration."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response(_build_auth_payload(user, token), status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """View for user login and token retrieval."""
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        """Handle user login and return auth payload with token."""
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
        """Authenticate the user with the provided credentials."""
        return authenticate(
            username=validated_data['username'],
            password=validated_data['password'],
        )
