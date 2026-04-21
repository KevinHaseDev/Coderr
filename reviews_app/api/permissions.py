from rest_framework.permissions import BasePermission

from profiles_app.models import Profile


class IsCustomerUser(BasePermission):
	"""Allow review creation only for authenticated customer users."""

	message = 'Only customer users can create reviews.'

	def has_permission(self, request, view):
		if not request.user or not request.user.is_authenticated:
			return False
		return Profile.objects.filter(
			user=request.user,
			user_type=Profile.TYPE_CUSTOMER,
		).exists()


class IsReviewOwner(BasePermission):
	"""Allow modifications and deletion only for the review creator."""

	message = 'Only the review owner can modify or delete this review.'

	def has_object_permission(self, request, view, obj):
		return bool(
			request.user
			and request.user.is_authenticated
			and obj.reviewer_id == request.user.id
		)
