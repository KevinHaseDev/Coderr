from rest_framework import serializers

from profiles_app.models import Profile
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
	"""Serialize review data for read and write endpoints with validation."""
	def validate_business_user(self, value):
		"""Validate that the business_user has a business profile."""
		try:
			profile = value.profile
		except Profile.DoesNotExist:
			raise serializers.ValidationError(
				'Der ausgewählte business_user hat kein Profil.',
			)

		if profile.user_type != Profile.TYPE_BUSINESS:
			raise serializers.ValidationError(
				'Der ausgewählte business_user muss ein Business-Profil haben.',
			)
		return value

	def validate(self, attrs):
		"""Validate that the reviewer has not already reviewed the same business user."""
		reviewer = self._get_reviewer(attrs)
		business_user = attrs.get('business_user') or getattr(
			self.instance,
			'business_user',
			None,
		)
		self._validate_duplicate_review(reviewer, business_user)
		return attrs

	def _get_reviewer(self, attrs):
		"""Extract the authenticated reviewer from the serializer context or fallback to existing value."""
		request = self.context.get('request')
		reviewer = getattr(request, 'user', None)
		if reviewer and reviewer.is_authenticated:
			return reviewer
		return attrs.get('reviewer') or getattr(self.instance, 'reviewer', None)

	def _validate_duplicate_review(self, reviewer, business_user):
		"""Validate that the reviewer has not already reviewed the same business user."""
		if not reviewer or not business_user:
			return
		duplicate_review = Review.objects.filter(
			reviewer=reviewer,
			business_user=business_user,
		)
		if self.instance is not None:
			duplicate_review = duplicate_review.exclude(pk=self.instance.pk)
		if duplicate_review.exists():
			raise serializers.ValidationError({
				'non_field_errors': [
					'Du hast diesen Business-User bereits bewertet.',
				],
			})

	class Meta:
		model = Review
		fields = [
			'id',
			'business_user',
			'reviewer',
			'rating',
			'description',
			'created_at',
			'updated_at',
		]
		read_only_fields = ['id', 'reviewer', 'created_at', 'updated_at']


class ReviewPatchSerializer(serializers.ModelSerializer):
	"""Serialize review data for PATCH endpoint with validation."""
	class Meta:
		model = Review
		fields = ['rating', 'description']

