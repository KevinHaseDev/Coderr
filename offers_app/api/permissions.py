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


class IsOfferOwner(BasePermission):
	"""Allow modifications only for the owner of an offer object."""

	message = 'Only the offer owner can modify this offer.'

	def has_object_permission(self, request, view, obj):
		return bool(
			request.user
			and request.user.is_authenticated
			and obj.user_id == request.user.id
		)
