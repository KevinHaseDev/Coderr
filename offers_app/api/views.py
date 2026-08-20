from decimal import Decimal, InvalidOperation

from django.db.models import Min, Q
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination

from offers_app.api.permissions import IsBusinessUser, IsOfferOwner
from offers_app.api.serializers import (
	OfferCreateSerializer,
	OfferDetailSerializer,
	OfferPatchSerializer,
	OfferSerializer,
)
from offers_app.models import Offer, OfferDetail


class OfferListPagination(PageNumberPagination):
	"""Paginate offer lists and allow per-request page size control."""

	page_size = 6
	page_size_query_param = 'page_size'
	max_page_size = 100


class OfferListView(generics.ListCreateAPIView):
	"""Return paginated offers with filtering, search, and ordering."""

	serializer_class = OfferSerializer
	pagination_class = OfferListPagination

	def get_serializer_class(self):
		"""Use a different serializer for offer creation to enforce detail requirements."""
		if self.request.method == 'POST':
			return OfferCreateSerializer
		return OfferSerializer

	def get_permissions(self):
		"""Return the appropriate permissions based on the request method."""
		if self.request.method == 'POST':
			return [permissions.IsAuthenticated(), IsBusinessUser()]
		return [permissions.AllowAny()]

	def perform_create(self, serializer):
		"""Save the new offer with the authenticated user as the owner."""
		serializer.save(user=self.request.user)

	def get_queryset(self):
		"""Return a queryset of offers with optional filtering, search, and ordering."""
		queryset = Offer.objects.select_related('user').prefetch_related('details')
		queryset = queryset.annotate(
			min_price=Min('details__price'),
			min_delivery_time=Min('details__delivery_time_in_days'),
		)
		queryset = self._filter_by_creator(queryset)
		queryset = self._filter_by_min_price(queryset)
		queryset = self._filter_by_max_delivery_time(queryset)
		queryset = self._apply_search(queryset)
		return self._apply_ordering(queryset)

	def _filter_by_creator(self, queryset):
		"""Filter offers by the creator's user ID."""
		creator_id = self._get_int_query_param('creator_id', min_value=1)
		if creator_id is None:
			return queryset
		return queryset.filter(user_id=creator_id)

	def _filter_by_min_price(self, queryset):
		"""Filter offers by the minimum price."""
		min_price = self._get_decimal_query_param('min_price', min_value=Decimal('0'))
		if min_price is None:
			return queryset
		return queryset.filter(min_price__gte=min_price)

	def _filter_by_max_delivery_time(self, queryset):
		"""Filter offers by the maximum delivery time."""
		max_delivery_time = self._get_int_query_param('max_delivery_time', min_value=1)
		if max_delivery_time is None:
			return queryset
		return queryset.filter(min_delivery_time__lte=max_delivery_time)

	def _apply_search(self, queryset):
		"""Apply a search filter on offer title and description."""
		search = self._get_query_param('search')
		if search is None:
			return queryset
		return queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))

	def _apply_ordering(self, queryset):
		"""Apply ordering to the queryset based on query parameters."""
		ordering = self._get_query_param('ordering') or '-updated_at'
		allowed = {'updated_at', '-updated_at', 'min_price', '-min_price'}
		if ordering not in allowed:
			raise ValidationError(
				{'ordering': "Allowed values are updated_at or min_price (optionally prefixed with '-')."}
			)
		return queryset.order_by(ordering, '-id')

	def _get_query_param(self, name):
		"""Return a stripped query parameter, or None when it is missing or empty."""
		raw_value = self.request.query_params.get(name)
		if raw_value is None:
			return None
		return raw_value.strip() or None

	def _get_int_query_param(self, name, min_value):
		"""Extract and validate an integer query parameter with a minimum value."""
		raw_value = self._get_query_param(name)
		if raw_value is None:
			return None
		try:
			value = int(raw_value)
		except (TypeError, ValueError):
			raise ValidationError({name: 'Must be an integer value.'})
		if value < min_value:
			raise ValidationError({name: f'Must be greater than or equal to {min_value}.'})
		return value

	def _get_decimal_query_param(self, name, min_value):
		"""Extract and validate a decimal query parameter with a minimum value."""
		raw_value = self._get_query_param(name)
		if raw_value is None:
			return None
		try:
			value = Decimal(raw_value)
		except (TypeError, InvalidOperation):
			raise ValidationError({name: 'Must be a decimal number.'})
		if value < min_value:
			raise ValidationError({name: f'Must be greater than or equal to {min_value}.'})
		return value


class OfferRetrieveView(generics.RetrieveUpdateDestroyAPIView):
	"""Return, partially update, or delete a single offer."""

	queryset = Offer.objects.select_related('user').prefetch_related('details')
	http_method_names = ['get', 'patch', 'delete', 'head', 'options']

	def get_serializer_class(self):
		"""Use a different serializer for PATCH requests to allow partial updates."""
		if self.request.method == 'PATCH':
			return OfferPatchSerializer
		return OfferSerializer

	def get_permissions(self):
		"""Return the appropriate permissions based on the request method."""
		if self.request.method in {'PATCH', 'DELETE'}:
			return [permissions.IsAuthenticated(), IsOfferOwner()]
		return [permissions.IsAuthenticated()]

	def partial_update(self, request, *args, **kwargs):
		"""Partially update an offer and return the updated data."""
		response = super().partial_update(request, *args, **kwargs)
		response.data = OfferSerializer(
			self.get_object(),
			context=self.get_serializer_context(),
		).data
		return response


class OfferDetailRetrieveView(generics.RetrieveAPIView):
	"""Return one offer detail object with all documented fields."""

	queryset = OfferDetail.objects.select_related('offer')
	serializer_class = OfferDetailSerializer
	permission_classes = [permissions.IsAuthenticated]
