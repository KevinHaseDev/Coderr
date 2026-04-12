from rest_framework.permissions import BasePermission

from profiles_app.models import Profile


class IsCustomerUser(BasePermission):
	"""Allow order creation only for authenticated customer users."""

	message = 'Only customer users can create orders.'

	def has_permission(self, request, view):
		if not request.user or not request.user.is_authenticated:
			return False
		return Profile.objects.filter(
			user=request.user,
			user_type=Profile.TYPE_CUSTOMER,
		).exists()


class IsAssignedBusinessUser(BasePermission):
	"""Allow status updates only for the assigned business user."""

	message = 'Only the assigned business user can update this order status.'

	def has_permission(self, request, view):
		if not request.user or not request.user.is_authenticated:
			return False
		return Profile.objects.filter(
			user=request.user,
			user_type=Profile.TYPE_BUSINESS,
		).exists()

	def has_object_permission(self, request, view, obj):
		return bool(
			request.user
			and request.user.is_authenticated
			and obj.business_user_id == request.user.id
		)


class IsStaffUserForDelete(BasePermission):
	"""Allow order deletion only for authenticated staff users."""

	message = 'Only staff users can delete orders.'

	def has_permission(self, request, view):
		return bool(
			request.user
			and request.user.is_authenticated
			and request.user.is_staff
		)

	def has_object_permission(self, request, view, obj):
		return self.has_permission(request, view)
