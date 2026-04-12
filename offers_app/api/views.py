from decimal import Decimal, InvalidOperation

from django.db.models import Min, Q
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination

from offers_app.api.serializers import OfferSerializer
from offers_app.models import Offer


class OfferListPagination(PageNumberPagination):
	"""Paginate offer lists and allow per-request page size control."""

	page_size = 6
	page_size_query_param = 'page_size'
	max_page_size = 100


class OfferListView(generics.ListAPIView):
	"""Return paginated offers with filtering, search, and ordering."""

	serializer_class = OfferSerializer
	permission_classes = [permissions.AllowAny]
	pagination_class = OfferListPagination

	def get_queryset(self):
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
		creator_id = self._get_int_query_param('creator_id', min_value=1)
		if creator_id is None:
			return queryset
		return queryset.filter(user_id=creator_id)

	def _filter_by_min_price(self, queryset):
		min_price = self._get_decimal_query_param('min_price', min_value=Decimal('0'))
		if min_price is None:
			return queryset
		return queryset.filter(min_price__gte=min_price)

	def _filter_by_max_delivery_time(self, queryset):
		max_delivery_time = self._get_int_query_param('max_delivery_time', min_value=1)
		if max_delivery_time is None:
			return queryset
		return queryset.filter(min_delivery_time__lte=max_delivery_time)

	def _apply_search(self, queryset):
		search = self.request.query_params.get('search', '').strip()
		if not search:
			return queryset
		return queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))

	def _apply_ordering(self, queryset):
		ordering = self.request.query_params.get('ordering', '-updated_at').strip()
		allowed = {'updated_at', 'min_price'}
		field = ordering.lstrip('-')
		if field not in allowed:
			raise ValidationError(
				{'ordering': "Allowed values are updated_at or min_price (optionally prefixed with '-')."}
			)
		return queryset.order_by(ordering, '-id')

	def _get_int_query_param(self, name, min_value):
		raw_value = self.request.query_params.get(name)
		if raw_value in (None, ''):
			return None
		try:
			value = int(raw_value)
		except (TypeError, ValueError):
			raise ValidationError({name: 'Must be an integer value.'})
		if value < min_value:
			raise ValidationError({name: f'Must be greater than or equal to {min_value}.'})
		return value

	def _get_decimal_query_param(self, name, min_value):
		raw_value = self.request.query_params.get(name)
		if raw_value in (None, ''):
			return None
		try:
			value = Decimal(raw_value)
		except (TypeError, InvalidOperation):
			raise ValidationError({name: 'Must be a decimal number.'})
		if value < min_value:
			raise ValidationError({name: f'Must be greater than or equal to {min_value}.'})
		return value
