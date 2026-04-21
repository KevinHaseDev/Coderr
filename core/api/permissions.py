"""Shared permission classes for role-based access checks."""

from rest_framework.permissions import BasePermission

from profiles_app.models import Profile


class IsRoleUser(BasePermission):
	"""Allow access only for authenticated users with a required role."""

	required_user_type = None
	message = 'This endpoint requires a specific profile role.'

	def has_permission(self, request, view):
		if not request.user or not request.user.is_authenticated:
			return False
		if self.required_user_type is None:
			return False
		return Profile.objects.filter(
			user=request.user,
			user_type=self.required_user_type,
		).exists()


class IsBusinessUser(IsRoleUser):
	"""Allow access only to authenticated users with a business profile."""

	required_user_type = Profile.TYPE_BUSINESS
	message = 'Only business users can access this endpoint.'


class IsCustomerUser(IsRoleUser):
	"""Allow access only to authenticated users with a customer profile."""

	required_user_type = Profile.TYPE_CUSTOMER
	message = 'Only customer users can access this endpoint.'