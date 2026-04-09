from rest_framework import serializers

from profiles_app.models import Profile


class ProfileDetailSerializer(serializers.ModelSerializer):
	"""Serialize and update profile details for a single user profile."""

	NON_NULL_RESPONSE_FIELDS = (
		'first_name',
		'last_name',
		'location',
		'tel',
		'description',
		'working_hours',
	)

	user = serializers.IntegerField(source='user.id', read_only=True)
	username = serializers.CharField(source='user.username', read_only=True)
	first_name = serializers.CharField(
		source='user.first_name', required=False, allow_blank=True
	)
	last_name = serializers.CharField(
		source='user.last_name', required=False, allow_blank=True
	)
	file = serializers.FileField(required=False, allow_null=True, use_url=False)
	tel = serializers.CharField(
		source='telephone', required=False, allow_blank=True
	)
	type = serializers.CharField(source='user_type', read_only=True)
	email = serializers.EmailField(
		source='user.email', required=False, allow_blank=True
	)

	class Meta:
		model = Profile
		fields = [
			'user',
			'username',
			'first_name',
			'last_name',
			'file',
			'location',
			'tel',
			'description',
			'working_hours',
			'type',
			'email',
			'created_at',
		]
		read_only_fields = ['user', 'username', 'type', 'created_at']

	def update(self, instance, validated_data):
		"""Update profile fields and related user fields in one request."""
		user_data = validated_data.pop('user', {})
		self._update_user(instance.user, user_data)
		for field, value in validated_data.items():
			setattr(instance, field, value)
		instance.save()
		return instance

	def to_representation(self, instance):
		"""Ensure required response fields are never serialized as null."""
		data = super().to_representation(instance)
		self._replace_none_with_blank(data)
		return data

	def _update_user(self, user, user_data):
		"""Persist nested user attributes if they were provided."""
		if not user_data:
			return
		for field, value in user_data.items():
			setattr(user, field, value)
		user.save()

	def _replace_none_with_blank(self, data):
		"""Normalize selected response fields from null to empty strings."""
		for field in self.NON_NULL_RESPONSE_FIELDS:
			if data.get(field) is None:
				data[field] = ''
