from django.contrib.auth import get_user_model
from django.db import models

from offers_app.models import OfferType

User = get_user_model()


class Order(models.Model):
	"""Snapshot order created from an offer detail."""

	STATUS_IN_PROGRESS = 'in_progress'
	STATUS_COMPLETED = 'completed'
	STATUS_CANCELLED = 'cancelled'
	STATUS_CHOICES = (
		(STATUS_IN_PROGRESS, 'In Progress'),
		(STATUS_COMPLETED, 'Completed'),
		(STATUS_CANCELLED, 'Cancelled'),
	)

	customer_user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='customer_orders',
	)
	business_user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='business_orders',
	)
	title = models.CharField(max_length=255)
	revisions = models.PositiveIntegerField()
	delivery_time_in_days = models.PositiveIntegerField()
	price = models.DecimalField(max_digits=10, decimal_places=2)
	features = models.JSONField(default=list)
	offer_type = models.CharField(max_length=20, choices=OfferType.choices)
	status = models.CharField(
		max_length=20,
		choices=STATUS_CHOICES,
		default=STATUS_IN_PROGRESS,
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f'Order #{self.pk} - {self.title}'
