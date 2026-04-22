from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from profiles_app.api.permissions import IsProfileOwner
from profiles_app.api.serializers import (
    BusinessProfileListSerializer,
    CustomerProfileListSerializer,
    ProfileDetailSerializer,
)
from profiles_app.models import Profile


class BusinessProfileListView(generics.ListAPIView):
    """Return all business profiles as a JSON array."""

    serializer_class = BusinessProfileListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    queryset = Profile.objects.select_related('user').filter(
        user_type=Profile.TYPE_BUSINESS,
    ).order_by('id')


class CustomerProfileListView(generics.ListAPIView):
    """Return all customer profiles as a JSON array."""

    serializer_class = CustomerProfileListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    queryset = Profile.objects.select_related('user').filter(
        user_type=Profile.TYPE_CUSTOMER,
    ).order_by('id')


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """Return and partially update a profile addressed by user id."""

    queryset = Profile.objects.select_related('user')
    serializer_class = ProfileDetailSerializer
    permission_classes = [IsAuthenticated, IsProfileOwner]
    lookup_field = 'user_id'
    lookup_url_kwarg = 'pk'
