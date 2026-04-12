from rest_framework.permissions import BasePermission

from profiles_app.models import Profile


class IsBusinessUser(BasePermission):
	"""Allow access only to authenticated users with a business profile."""

	message = 'Only business users can create offers.'

	def has_permission(self, request, view):
		if not request.user or not request.user.is_authenticated:
			return False
		return Profile.objects.filter(
			user=request.user,
			user_type=Profile.TYPE_BUSINESS,
		).exists()
