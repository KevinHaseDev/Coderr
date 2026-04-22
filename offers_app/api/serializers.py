from django.db import transaction
from django.db.models import Min
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailUrlSerializer(serializers.ModelSerializer):
	"""Serialize nested offer detail references as id and URL."""

	url = serializers.SerializerMethodField()

	class Meta:
		model = OfferDetail
		fields = ['id', 'url']

	def get_url(self, obj):
		"""Return detail URL as absolute when request context is available."""
		request = self.context.get('request')
		path = f'/api/offerdetails/{obj.id}/'
		if request is None:
			return path
		return request.build_absolute_uri(path)


class OfferDetailSerializer(serializers.ModelSerializer):
	"""Serialize full offer detail payloads."""

	class Meta:
		model = OfferDetail
		fields = [
			'id',
			'title',
			'revisions',
			'delivery_time_in_days',
			'price',
			'features',
			'offer_type',
		]
		read_only_fields = ['id']


class OfferCreateSerializer(serializers.ModelSerializer):
	"""Create offers with exactly three uniquely typed details."""

	details = OfferDetailSerializer(many=True)

	class Meta:
		model = Offer
		fields = ['id', 'title', 'image', 'description', 'details']
		read_only_fields = ['id']

	def validate_details(self, value):
		"""Validate that exactly three details with unique offer types are provided."""
		if len(value) != 3:
			raise serializers.ValidationError('Exactly 3 details are required.')
		offer_types = [detail['offer_type'] for detail in value]
		if len(set(offer_types)) != len(offer_types):
			raise serializers.ValidationError('offer_type must be unique within details.')
		return value

	def create(self, validated_data):
		"""Create an offer with its associated details."""
		details_data = validated_data.pop('details')
		with transaction.atomic():
			offer = Offer.objects.create(**validated_data)
			OfferDetail.objects.bulk_create(
				[OfferDetail(offer=offer, **detail_data) for detail_data in details_data]
			)
		return offer


class OfferDetailPatchSerializer(serializers.ModelSerializer):
	"""Serialize partial updates for a single offer detail."""

	class Meta:
		model = OfferDetail
		fields = [
			'title',
			'revisions',
			'delivery_time_in_days',
			'price',
			'features',
			'offer_type',
		]
		extra_kwargs = {
			'title': {'required': False},
			'revisions': {'required': False},
			'delivery_time_in_days': {'required': False},
			'price': {'required': False},
			'features': {'required': False},
			'offer_type': {'required': False},
		}


class OfferPatchSerializer(serializers.ModelSerializer):
	"""Partially update an offer and selected details by offer_type."""

	details = OfferDetailPatchSerializer(many=True, required=False)

	class Meta:
		model = Offer
		fields = ['title', 'image', 'description', 'details']
		extra_kwargs = {
			'title': {'required': False},
			'image': {'required': False},
			'description': {'required': False},
		}

	def validate_details(self, value):
		"""Validate that provided details have unique offer types."""
		offer_types = []
		for index, detail in enumerate(value):
			detail_type = detail.get('offer_type')
			if not detail_type:
				raise serializers.ValidationError({index: {'offer_type': 'This field is required.'}})
			offer_types.append(detail_type)
		if len(set(offer_types)) != len(offer_types):
			raise serializers.ValidationError('offer_type must be unique within details.')
		return value

	def update(self, instance, validated_data):
		"""Update offer fields and optionally its details within a transaction."""
		details_data = validated_data.pop('details', None)
		with transaction.atomic():
			self._update_offer_fields(instance, validated_data)
			if details_data is not None:
				self._update_offer_details(instance, details_data)
		return instance

	def _update_offer_fields(self, instance, validated_data):
		"""Update offer fields with validated data."""
		for field, value in validated_data.items():
			setattr(instance, field, value)
		instance.save()

	def _update_offer_details(self, instance, details_data):
		"""Update offer details with validated data."""
		details_by_type = {detail.offer_type: detail for detail in instance.details.all()}
		for detail_data in details_data:
			detail_data = dict(detail_data)
			detail_type = detail_data.pop('offer_type')
			detail_instance = details_by_type.get(detail_type)
			if detail_instance is None:
				raise serializers.ValidationError(
					{'details': f"No detail found for offer_type '{detail_type}'."}
				)
			for field, value in detail_data.items():
				setattr(detail_instance, field, value)
			if detail_data:
				detail_instance.save()


class OfferSerializer(serializers.ModelSerializer):
	"""Serialize offers with nested detail URLs and aggregated minima."""

	details = OfferDetailUrlSerializer(many=True, read_only=True)
	min_price = serializers.SerializerMethodField()
	min_delivery_time = serializers.SerializerMethodField()

	class Meta:
		model = Offer
		fields = [
			'id',
			'user',
			'title',
			'image',
			'description',
			'created_at',
			'updated_at',
			'details',
			'min_price',
			'min_delivery_time',
		]
		read_only_fields = [
			'id',
			'user',
			'created_at',
			'updated_at',
			'min_price',
			'min_delivery_time',
		]

	def get_min_price(self, obj):
		"""Expose minimum price across all related offer details."""
		return self._get_detail_minima(obj)['min_price']

	def get_min_delivery_time(self, obj):
		"""Expose shortest delivery time across related offer details."""
		return self._get_detail_minima(obj)['min_delivery_time']

	def _get_detail_minima(self, obj):
		"""Cache aggregate minima per offer for repeated serializer access."""
		minima = getattr(obj, '_detail_minima', None)
		if minima is None:
			minima = obj.details.aggregate(
				min_price=Min('price'),
				min_delivery_time=Min('delivery_time_in_days'),
			)
			setattr(obj, '_detail_minima', minima)
		return minima
