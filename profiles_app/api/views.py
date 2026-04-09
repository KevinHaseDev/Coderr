from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from profiles_app.api.permissions import IsProfileOwner
from profiles_app.api.serializers import ProfileDetailSerializer
from profiles_app.models import Profile


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """Return and partially update a profile addressed by user id."""

    queryset = Profile.objects.select_related('user')
    serializer_class = ProfileDetailSerializer
    permission_classes = [IsAuthenticated, IsProfileOwner]
    lookup_field = 'user_id'
    lookup_url_kwarg = 'pk'
