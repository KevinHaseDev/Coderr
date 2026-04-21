from rest_framework import serializers

from profiles_app.models import Profile
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
	def validate_business_user(self, value):
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
		request = self.context.get('request')
		reviewer = getattr(request, 'user', None)
		if reviewer is None or not reviewer.is_authenticated:
			reviewer = attrs.get('reviewer') or getattr(self.instance, 'reviewer', None)

		business_user = attrs.get('business_user') or getattr(
			self.instance,
			'business_user',
			None,
		)
		if reviewer and business_user:
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
		return attrs

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
	class Meta:
		model = Review
		fields = ['rating', 'description']

