from rest_framework import serializers

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderReadSerializer(serializers.ModelSerializer):
	"""Serialize full order response payload for read endpoints."""

	class Meta:
		model = Order
		fields = [
			'id',
			'customer_user',
			'business_user',
			'title',
			'revisions',
			'delivery_time_in_days',
			'price',
			'features',
			'offer_type',
			'status',
			'created_at',
			'updated_at',
		]


class OrderCreateSerializer(serializers.ModelSerializer):
	"""Create an order snapshot from a selected offer detail."""

	offer_detail_id = serializers.PrimaryKeyRelatedField(
		source='offer_detail',
		queryset=OfferDetail.objects.select_related('offer__user'),
		write_only=True,
	)

	class Meta:
		model = Order
		fields = [
			'id',
			'offer_detail_id',
			'customer_user',
			'business_user',
			'title',
			'revisions',
			'delivery_time_in_days',
			'price',
			'features',
			'offer_type',
			'status',
			'created_at',
			'updated_at',
		]
		read_only_fields = [
			'id',
			'customer_user',
			'business_user',
			'title',
			'revisions',
			'delivery_time_in_days',
			'price',
			'features',
			'offer_type',
			'status',
			'created_at',
			'updated_at',
		]

	def create(self, validated_data):
		offer_detail = validated_data.pop('offer_detail')
		customer_user = validated_data.pop('customer_user', None)

		if customer_user is None:
			request = self.context.get('request')
			if request and request.user and request.user.is_authenticated:
				customer_user = request.user

		if customer_user is None:
			raise serializers.ValidationError(
				{'offer_detail_id': 'Authenticated customer user is required.'}
			)

		return Order.objects.create(
			customer_user=customer_user,
			business_user=offer_detail.offer.user,
			title=offer_detail.title,
			revisions=offer_detail.revisions,
			delivery_time_in_days=offer_detail.delivery_time_in_days,
			price=offer_detail.price,
			features=offer_detail.features,
			offer_type=offer_detail.offer_type,
		)
		read_only_fields = [
			'id',
			'customer_user',
			'business_user',
			'title',
			'revisions',
			'delivery_time_in_days',
			'price',
			'features',
			'offer_type',
			'status',
			'created_at',
			'updated_at',
		]
