"""Tests for order list endpoint behavior."""

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import include, path
from rest_framework import status
from rest_framework.test import APITestCase

from orders_app.models import Order

urlpatterns = [
	path('api/', include('orders_app.api.urls')),
]

User = get_user_model()


@override_settings(ROOT_URLCONF='orders_app.tests.test_orders_app')
class OrderListApiTests(APITestCase):
	"""Validate GET /api/orders/ auth and ownership filtering."""

	LIST_URL = '/api/orders/'

	def setUp(self):
		self.user = User.objects.create_user(
			username='orders_user',
			email='orders_user@example.com',
			password='StrongPass123',
		)
		self.other_user = User.objects.create_user(
			username='other_user',
			email='other_user@example.com',
			password='StrongPass123',
		)
		self.third_user = User.objects.create_user(
			username='third_user',
			email='third_user@example.com',
			password='StrongPass123',
		)

	def _create_order(self, customer_user, business_user, title):
		return Order.objects.create(
			customer_user=customer_user,
			business_user=business_user,
			title=title,
			revisions=2,
			delivery_time_in_days=5,
			price='150.00',
			features=['Logo Design'],
			offer_type=Order.OFFER_TYPE_BASIC,
			status=Order.STATUS_IN_PROGRESS,
		)

	def test_get_orders_requires_authentication(self):
		"""Anonymous requests must be rejected with HTTP 401."""
		response = self.client.get(self.LIST_URL)
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_get_orders_returns_only_authenticated_user_orders(self):
		"""Return orders where user is either customer_user or business_user."""
		customer_order = self._create_order(
			customer_user=self.user,
			business_user=self.other_user,
			title='User As Customer',
		)
		business_order = self._create_order(
			customer_user=self.other_user,
			business_user=self.user,
			title='User As Business',
		)
		unrelated_order = self._create_order(
			customer_user=self.other_user,
			business_user=self.third_user,
			title='Unrelated Order',
		)

		self.client.force_authenticate(user=self.user)
		response = self.client.get(self.LIST_URL)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 2)

		returned_ids = {item['id'] for item in response.data}
		self.assertSetEqual(
			returned_ids,
			{customer_order.id, business_order.id},
		)
		self.assertNotIn(unrelated_order.id, returned_ids)
