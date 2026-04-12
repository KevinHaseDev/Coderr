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
