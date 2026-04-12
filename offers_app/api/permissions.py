from rest_framework.permissions import BasePermission

from profiles_app.models import Profile


class IsBusinessUser(BasePermission):
	"""Allow access only to authenticated users with a business profile."""

	message = 'Only business users can create offers.'

	def has_permission(self, request, view):
		profile = getattr(request.user, 'profile', None)
		return bool(profile and profile.user_type == Profile.TYPE_BUSINESS)
