from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from reviews_app.api.permissions import IsCustomerUser
from reviews_app.api.serializers import ReviewSerializer
from reviews_app.models import Review


class ReviewsAppStatusView(ListCreateAPIView):
	"""List reviews for authenticated users with optional filtering and ordering."""

	permission_classes = [IsAuthenticated]
	serializer_class = ReviewSerializer
	queryset = Review.objects.all()

	def get_permissions(self):
		if self.request.method == 'POST':
			return [IsCustomerUser()]
		return [IsAuthenticated()]

	def perform_create(self, serializer):
		serializer.save(reviewer=self.request.user)

	def get_queryset(self):
		queryset = self._get_filtered_queryset()
		ordering = self.request.query_params.get('ordering')
		if not ordering:
			return queryset
		if ordering not in {'updated_at', '-updated_at', 'rating', '-rating'}:
			raise ValidationError({
				'ordering': 'Ungültiger ordering-Wert. Erlaubt sind: updated_at, -updated_at, rating, -rating.',
			})
		return queryset.order_by(ordering)

	def _get_filtered_queryset(self):
		queryset = self.queryset
		business_user_id = self.request.query_params.get('business_user_id')
		reviewer_id = self.request.query_params.get('reviewer_id')
		if business_user_id:
			queryset = queryset.filter(business_user_id=business_user_id)
		if reviewer_id:
			queryset = queryset.filter(reviewer_id=reviewer_id)
		return queryset
