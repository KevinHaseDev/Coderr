from django.db.models import Q
from rest_framework import generics, permissions

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


class OrderUpdateDeleteView(generics.UpdateDestroyAPIView):
	"""Allow PATCH status updates and DELETE on a specific order."""

	queryset = Order.objects.select_related('customer_user', 'business_user')
	http_method_names = ['patch', 'delete', 'head', 'options']

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
