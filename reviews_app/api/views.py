from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from reviews_app.api.permissions import IsCustomerUser, IsReviewOwner
from reviews_app.api.serializers import ReviewPatchSerializer, ReviewSerializer
from reviews_app.models import Review


class ReviewListCreateView(ListCreateAPIView):
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
		queryset = self.queryset.all()
		business_user_id = self.request.query_params.get('business_user_id')
		reviewer_id = self.request.query_params.get('reviewer_id')
		if business_user_id:
			queryset = queryset.filter(business_user_id=business_user_id)
		if reviewer_id:
			queryset = queryset.filter(reviewer_id=reviewer_id)
		return queryset


class ReviewUpdateDeleteView(RetrieveUpdateDestroyAPIView):
	"""Allow PATCH and DELETE for a specific review owned by the requester."""

	queryset = Review.objects.all()
	http_method_names = ['patch', 'delete', 'head', 'options']

	def get_serializer_class(self):
		if self.request.method == 'PATCH':
			return ReviewPatchSerializer
		return ReviewSerializer

	def get_permissions(self):
		return [IsAuthenticated(), IsReviewOwner()]

	def partial_update(self, request, *args, **kwargs):
		response = super().partial_update(request, *args, **kwargs)
		response.data = ReviewSerializer(
			self.get_object(),
			context=self.get_serializer_context(),
		).data
		return response
