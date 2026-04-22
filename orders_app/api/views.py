from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from orders_app.api.permissions import (
	IsAssignedBusinessUser,
	IsCustomerUser,
	IsStaffUserForDelete,
)
from orders_app.api.serializers import (
	OrderCreateSerializer,
	OrderReadSerializer,
	OrderStatusPatchSerializer,
)
from orders_app.models import Order
from profiles_app.models import Profile


class OrderListCreateView(generics.ListCreateAPIView):
	"""List user-related orders and allow customer users to create orders."""

	queryset = Order.objects.select_related('customer_user', 'business_user')
	http_method_names = ['get', 'post', 'head', 'options']

	def get_serializer_class(self):
		"""Return the appropriate serializer class based on the HTTP method."""
		if self.request.method == 'POST':
			return OrderCreateSerializer
		return OrderReadSerializer

	def get_permissions(self):
		"""Return permission classes based on the HTTP method."""
		if self.request.method == 'POST':
			return [permissions.IsAuthenticated(), IsCustomerUser()]
		return [permissions.IsAuthenticated()]

	def get_queryset(self):
		"""Return orders related to the authenticated user, ordered by most recent updates."""
		user = self.request.user
		return self.queryset.filter(
			Q(customer_user=user) | Q(business_user=user)
		).order_by('-updated_at', '-id')


class OrderUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
	"""Allow PATCH status updates and DELETE on a specific order."""

	queryset = Order.objects.select_related('customer_user', 'business_user')
	http_method_names = ['get', 'patch', 'delete', 'head', 'options']

	def get_serializer_class(self):
		"""Return the appropriate serializer class based on the HTTP method."""
		if self.request.method == 'PATCH':
			return OrderStatusPatchSerializer
		return OrderReadSerializer

	def get_permissions(self):
		"""Return permission classes based on the HTTP method."""
		if self.request.method == 'PATCH':
			return [permissions.IsAuthenticated(), IsAssignedBusinessUser()]
		if self.request.method == 'DELETE':
			return [permissions.IsAuthenticated(), IsStaffUserForDelete()]
		return [permissions.IsAuthenticated()]

	def partial_update(self, request, *args, **kwargs):
		"""Override partial_update to return the full order data after status update."""
		response = super().partial_update(request, *args, **kwargs)
		response.data = OrderReadSerializer(
			self.get_object(),
			context=self.get_serializer_context(),
		).data
		return response


class BaseOrderCountView(generics.GenericAPIView):
	"""Return a status-specific order count for a business user."""

	permission_classes = [permissions.IsAuthenticated]
	status = None
	response_key = 'order_count'

	def get(self, request, business_user_id):
		"""Return the count of orders for the specified business user and status."""
		self._ensure_business_profile_exists(business_user_id)
		order_count = self._get_order_count(business_user_id)
		return Response({self.response_key: order_count})

	def _ensure_business_profile_exists(self, business_user_id):
		"""Check that a business profile exists for the specified user id."""
		if not Profile.objects.filter(
			user_id=business_user_id,
			user_type=Profile.TYPE_BUSINESS,
		).exists():
			raise NotFound('No business user found with the provided id.')

	def _get_order_count(self, business_user_id):
		"""Return the count of orders for the specified business user and status."""
		return Order.objects.filter(
			business_user_id=business_user_id,
			status=self.status,
		).count()


class OrderCountView(BaseOrderCountView):
	"""Return count of in-progress orders for a business user."""

	status = Order.STATUS_IN_PROGRESS
	response_key = 'order_count'


class CompletedOrderCountView(BaseOrderCountView):
	"""Return count of completed orders for a business user."""

	status = Order.STATUS_COMPLETED
	response_key = 'completed_order_count'
