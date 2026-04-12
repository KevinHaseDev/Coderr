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
		if self.request.method == 'POST':
			return OrderCreateSerializer
		return OrderReadSerializer

	def get_permissions(self):
		if self.request.method == 'POST':
			return [permissions.IsAuthenticated(), IsCustomerUser()]
		return [permissions.IsAuthenticated()]

	def get_queryset(self):
		user = self.request.user
		return self.queryset.filter(
			Q(customer_user=user) | Q(business_user=user)
		).order_by('-updated_at', '-id')

	def perform_create(self, serializer):
		offer_detail = serializer.validated_data['offer_detail']
		serializer.instance = Order.objects.create(
			customer_user=self.request.user,
			business_user=offer_detail.offer.user,
			title=offer_detail.title,
			revisions=offer_detail.revisions,
			delivery_time_in_days=offer_detail.delivery_time_in_days,
			price=offer_detail.price,
			features=offer_detail.features,
			offer_type=offer_detail.offer_type,
		)


class OrderUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
	"""Allow PATCH status updates and DELETE on a specific order."""

	queryset = Order.objects.select_related('customer_user', 'business_user')
	http_method_names = ['get', 'patch', 'delete', 'head', 'options']

	def get_serializer_class(self):
		if self.request.method == 'PATCH':
			return OrderStatusPatchSerializer
		return OrderReadSerializer

	def get_permissions(self):
		if self.request.method == 'PATCH':
			return [permissions.IsAuthenticated(), IsAssignedBusinessUser()]
		if self.request.method == 'DELETE':
			return [permissions.IsAuthenticated(), IsStaffUserForDelete()]
		return [permissions.IsAuthenticated()]

	def partial_update(self, request, *args, **kwargs):
		response = super().partial_update(request, *args, **kwargs)
		response.data = OrderReadSerializer(
			self.get_object(),
			context=self.get_serializer_context(),
		).data
		return response


class OrderCountView(generics.GenericAPIView):
	"""Return count of in-progress orders for a business user."""

	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, business_user_id):
		if not Profile.objects.filter(
			user_id=business_user_id,
			user_type=Profile.TYPE_BUSINESS,
		).exists():
			raise NotFound('No business user found with the provided id.')

		order_count = Order.objects.filter(
			business_user_id=business_user_id,
			status=Order.STATUS_IN_PROGRESS,
		).count()
		return Response({'order_count': order_count})


class CompletedOrderCountView(generics.GenericAPIView):
	"""Return count of completed orders for a business user."""

	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, business_user_id):
		if not Profile.objects.filter(
			user_id=business_user_id,
			user_type=Profile.TYPE_BUSINESS,
		).exists():
			raise NotFound('No business user found with the provided id.')

		completed_order_count = Order.objects.filter(
			business_user_id=business_user_id,
			status=Order.STATUS_COMPLETED,
		).count()
		return Response({'completed_order_count': completed_order_count})
