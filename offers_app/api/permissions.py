from rest_framework.permissions import BasePermission

from profiles_app.api.permissions import IsBusinessUser


class IsOfferOwner(BasePermission):
	"""Allow modifications and deletion only for the offer owner."""

	message = 'Only the offer owner can modify or delete this offer.'

	def has_object_permission(self, request, view, obj):
		"""Grant permission only when request user owns the target offer."""
		return bool(
			request.user
			and request.user.is_authenticated
			and obj.user_id == request.user.id
		)
