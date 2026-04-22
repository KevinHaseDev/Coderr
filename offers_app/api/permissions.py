from rest_framework.permissions import BasePermission

from profiles_app.api.permissions import IsBusinessUser


class IsOfferOwner(BasePermission):
	"""Allow modifications and deletion only for the offer owner."""

	message = 'Only the offer owner can modify or delete this offer.'

	def has_object_permission(self, request, view, obj):
		return bool(
			request.user
			and request.user.is_authenticated
			and obj.user_id == request.user.id
		)
