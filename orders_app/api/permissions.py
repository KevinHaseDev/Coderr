from rest_framework.permissions import BasePermission

from profiles_app.api.permissions import IsBusinessUser, IsCustomerUser


class IsAssignedBusinessUser(BasePermission):
	"""Allow status updates only for the assigned business user."""

	message = 'Only the assigned business user can update this order status.'

	def has_permission(self, request, view):
		return IsBusinessUser().has_permission(request, view)

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
