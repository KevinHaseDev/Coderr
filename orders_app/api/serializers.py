from rest_framework import serializers

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
