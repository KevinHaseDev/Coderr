from rest_framework.permissions import BasePermission

from core.api.permissions import IsCustomerUser


class IsReviewOwner(BasePermission):
	"""Allow modifications and deletion only for the review creator."""

	message = 'Only the review owner can modify or delete this review.'

	def has_object_permission(self, request, view, obj):
		return bool(
			request.user
			and request.user.is_authenticated
			and obj.reviewer_id == request.user.id
		)
