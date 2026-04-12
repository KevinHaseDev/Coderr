"""Tests for order list endpoint behavior."""

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import include, path
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from profiles_app.models import Profile

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


@override_settings(ROOT_URLCONF='orders_app.tests.test_orders_app')
class OrderCreateApiTests(APITestCase):
	"""Validate POST /api/orders/ create behavior."""

	LIST_URL = '/api/orders/'

	def setUp(self):
		self.customer_user = User.objects.create_user(
			username='customer_for_post',
			email='customer_for_post@example.com',
			password='StrongPass123',
		)
		self.business_user = User.objects.create_user(
			username='business_for_post',
			email='business_for_post@example.com',
			password='StrongPass123',
		)

		Profile.objects.create(
			user=self.customer_user,
			user_type=Profile.TYPE_CUSTOMER,
		)
		Profile.objects.create(
			user=self.business_user,
			user_type=Profile.TYPE_BUSINESS,
		)

		offer = Offer.objects.create(
			user=self.business_user,
			title='Logo Offer',
			description='Offer description',
			image=None,
		)
		self.offer_detail = OfferDetail.objects.create(
			offer=offer,
			title='Basic Logo',
			revisions=2,
			delivery_time_in_days=5,
			price='150.00',
			features=['Logo Design'],
			offer_type=OfferDetail.OFFER_TYPE_BASIC,
		)

	def test_post_orders_creates_order_from_offer_detail(self):
		"""Customer can create order snapshot from offer_detail_id."""
		self.client.force_authenticate(user=self.customer_user)
		response = self.client.post(
			self.LIST_URL,
			{'offer_detail_id': self.offer_detail.id},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Order.objects.count(), 1)

		order = Order.objects.get()
		self.assertEqual(order.customer_user, self.customer_user)
		self.assertEqual(order.business_user, self.business_user)
		self.assertEqual(order.title, self.offer_detail.title)
		self.assertEqual(order.offer_type, self.offer_detail.offer_type)
		self.assertEqual(order.status, Order.STATUS_IN_PROGRESS)

		self.assertEqual(response.data['id'], order.id)
		self.assertEqual(response.data['customer_user'], self.customer_user.id)
		self.assertEqual(response.data['business_user'], self.business_user.id)

	def test_post_orders_returns_400_when_offer_detail_id_missing(self):
		"""offer_detail_id is required for order creation."""
		self.client.force_authenticate(user=self.customer_user)
		response = self.client.post(self.LIST_URL, {}, format='json')

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('offer_detail_id', response.data)

	def test_post_orders_returns_400_for_invalid_offer_detail_id(self):
		"""Unknown offer_detail_id should fail validation."""
		self.client.force_authenticate(user=self.customer_user)
		response = self.client.post(
			self.LIST_URL,
			{'offer_detail_id': 999999},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('offer_detail_id', response.data)

	def test_post_orders_forbidden_for_non_customer_user(self):
		"""Only users with customer profile can create orders."""
		self.client.force_authenticate(user=self.business_user)
		response = self.client.post(
			self.LIST_URL,
			{'offer_detail_id': self.offer_detail.id},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@override_settings(ROOT_URLCONF='orders_app.tests.test_orders_app')
class OrderPatchApiTests(APITestCase):
	"""Validate PATCH /api/orders/{id}/ permission and validation behavior."""

	def setUp(self):
		self.customer_user = User.objects.create_user(
			username='customer_for_patch',
			email='customer_for_patch@example.com',
			password='StrongPass123',
		)
		self.business_user = User.objects.create_user(
			username='business_for_patch',
			email='business_for_patch@example.com',
			password='StrongPass123',
		)
		self.other_business_user = User.objects.create_user(
			username='other_business_for_patch',
			email='other_business_for_patch@example.com',
			password='StrongPass123',
		)

		Profile.objects.create(
			user=self.customer_user,
			user_type=Profile.TYPE_CUSTOMER,
		)
		Profile.objects.create(
			user=self.business_user,
			user_type=Profile.TYPE_BUSINESS,
		)
		Profile.objects.create(
			user=self.other_business_user,
			user_type=Profile.TYPE_BUSINESS,
		)

		self.order = Order.objects.create(
			customer_user=self.customer_user,
			business_user=self.business_user,
			title='Patchable Order',
			revisions=2,
			delivery_time_in_days=5,
			price='150.00',
			features=['Logo Design'],
			offer_type=Order.OFFER_TYPE_BASIC,
			status=Order.STATUS_IN_PROGRESS,
		)
		self.url = f'/api/orders/{self.order.id}/'

	def test_patch_order_status_allowed_for_assigned_business_user(self):
		"""Assigned business user can update order status."""
		self.client.force_authenticate(user=self.business_user)
		response = self.client.patch(
			self.url,
			{'status': Order.STATUS_COMPLETED},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.order.refresh_from_db()
		self.assertEqual(self.order.status, Order.STATUS_COMPLETED)

	def test_patch_order_status_forbidden_for_non_assigned_business_user(self):
		"""Different business user must not update foreign order status."""
		self.client.force_authenticate(user=self.other_business_user)
		response = self.client.patch(
			self.url,
			{'status': Order.STATUS_COMPLETED},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_patch_order_status_rejects_invalid_status(self):
		"""Invalid status value must return HTTP 400."""
		self.client.force_authenticate(user=self.business_user)
		response = self.client.patch(
			self.url,
			{'status': 'not_a_valid_status'},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('status', response.data)

	def test_patch_order_status_returns_404_for_unknown_order(self):
		"""Patching a missing order id must return HTTP 404."""
		self.client.force_authenticate(user=self.business_user)
		response = self.client.patch(
			'/api/orders/999999/',
			{'status': Order.STATUS_COMPLETED},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@override_settings(ROOT_URLCONF='orders_app.tests.test_orders_app')
class OrderDeleteApiTests(APITestCase):
	"""Validate DELETE /api/orders/{id}/ permission and response behavior."""

	def setUp(self):
		self.customer_user = User.objects.create_user(
			username='customer_for_delete',
			email='customer_for_delete@example.com',
			password='StrongPass123',
		)
		self.business_user = User.objects.create_user(
			username='business_for_delete',
			email='business_for_delete@example.com',
			password='StrongPass123',
		)
		self.staff_user = User.objects.create_user(
			username='staff_for_delete',
			email='staff_for_delete@example.com',
			password='StrongPass123',
			is_staff=True,
		)

		Profile.objects.create(
			user=self.customer_user,
			user_type=Profile.TYPE_CUSTOMER,
		)
		Profile.objects.create(
			user=self.business_user,
			user_type=Profile.TYPE_BUSINESS,
		)

		self.order = Order.objects.create(
			customer_user=self.customer_user,
			business_user=self.business_user,
			title='Deletable Order',
			revisions=2,
			delivery_time_in_days=5,
			price='150.00',
			features=['Logo Design'],
			offer_type=Order.OFFER_TYPE_BASIC,
			status=Order.STATUS_IN_PROGRESS,
		)
		self.url = f'/api/orders/{self.order.id}/'

	def test_delete_order_forbidden_for_non_staff_user(self):
		"""Non-staff users must not be allowed to delete orders."""
		self.client.force_authenticate(user=self.business_user)
		response = self.client.delete(self.url)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_delete_order_returns_204_for_staff_user(self):
		"""Staff user can delete order and receives HTTP 204 with empty body."""
		self.client.force_authenticate(user=self.staff_user)
		response = self.client.delete(self.url)

		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(response.content, b'')
		self.assertFalse(Order.objects.filter(id=self.order.id).exists())

	def test_delete_order_returns_404_for_unknown_order(self):
		"""Deleting a non-existing order id must return HTTP 404."""
		self.client.force_authenticate(user=self.staff_user)
		response = self.client.delete('/api/orders/999999/')

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@override_settings(ROOT_URLCONF='orders_app.tests.test_orders_app')
class OrderCountApiTests(APITestCase):
	"""Validate GET /api/order-count/{business_user_id}/ behavior."""

	def setUp(self):
		self.auth_user = User.objects.create_user(
			username='count_auth_user',
			email='count_auth_user@example.com',
			password='StrongPass123',
		)
		self.business_user = User.objects.create_user(
			username='count_business_user',
			email='count_business_user@example.com',
			password='StrongPass123',
		)
		self.other_business_user = User.objects.create_user(
			username='count_other_business_user',
			email='count_other_business_user@example.com',
			password='StrongPass123',
		)

		Profile.objects.create(
			user=self.auth_user,
			user_type=Profile.TYPE_CUSTOMER,
		)
		Profile.objects.create(
			user=self.business_user,
			user_type=Profile.TYPE_BUSINESS,
		)
		Profile.objects.create(
			user=self.other_business_user,
			user_type=Profile.TYPE_BUSINESS,
		)

		Order.objects.create(
			customer_user=self.auth_user,
			business_user=self.business_user,
			title='In Progress 1',
			revisions=2,
			delivery_time_in_days=5,
			price='100.00',
			features=['Feature A'],
			offer_type=Order.OFFER_TYPE_BASIC,
			status=Order.STATUS_IN_PROGRESS,
		)
		Order.objects.create(
			customer_user=self.auth_user,
			business_user=self.business_user,
			title='In Progress 2',
			revisions=2,
			delivery_time_in_days=5,
			price='120.00',
			features=['Feature B'],
			offer_type=Order.OFFER_TYPE_STANDARD,
			status=Order.STATUS_IN_PROGRESS,
		)
		Order.objects.create(
			customer_user=self.auth_user,
			business_user=self.business_user,
			title='Completed Ignored',
			revisions=2,
			delivery_time_in_days=5,
			price='140.00',
			features=['Feature C'],
			offer_type=Order.OFFER_TYPE_PREMIUM,
			status=Order.STATUS_COMPLETED,
		)
		Order.objects.create(
			customer_user=self.auth_user,
			business_user=self.other_business_user,
			title='Other Business Ignored',
			revisions=2,
			delivery_time_in_days=5,
			price='160.00',
			features=['Feature D'],
			offer_type=Order.OFFER_TYPE_BASIC,
			status=Order.STATUS_IN_PROGRESS,
		)

	def test_order_count_requires_authentication(self):
		"""Anonymous requests must be rejected with HTTP 401."""
		response = self.client.get(f'/api/order-count/{self.business_user.id}/')

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_order_count_returns_correct_in_progress_count(self):
		"""Endpoint must return only in-progress orders for target business user."""
		self.client.force_authenticate(user=self.auth_user)
		response = self.client.get(f'/api/order-count/{self.business_user.id}/')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data, {'order_count': 2})

	def test_order_count_returns_404_for_unknown_business_user(self):
		"""Unknown business user id must return HTTP 404."""
		self.client.force_authenticate(user=self.auth_user)
		response = self.client.get('/api/order-count/999999/')

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@override_settings(ROOT_URLCONF='orders_app.tests.test_orders_app')
class CompletedOrderCountApiTests(APITestCase):
	"""Validate GET /api/completed-order-count/{business_user_id}/ behavior."""

	def setUp(self):
		self.auth_user = User.objects.create_user(
			username='completed_count_auth_user',
			email='completed_count_auth_user@example.com',
			password='StrongPass123',
		)
		self.business_user = User.objects.create_user(
			username='completed_count_business_user',
			email='completed_count_business_user@example.com',
			password='StrongPass123',
		)
		self.other_business_user = User.objects.create_user(
			username='completed_count_other_business_user',
			email='completed_count_other_business_user@example.com',
			password='StrongPass123',
		)

		Profile.objects.create(
			user=self.auth_user,
			user_type=Profile.TYPE_CUSTOMER,
		)
		Profile.objects.create(
			user=self.business_user,
			user_type=Profile.TYPE_BUSINESS,
		)
		Profile.objects.create(
			user=self.other_business_user,
			user_type=Profile.TYPE_BUSINESS,
		)

		Order.objects.create(
			customer_user=self.auth_user,
			business_user=self.business_user,
			title='Completed 1',
			revisions=2,
			delivery_time_in_days=5,
			price='210.00',
			features=['Feature E'],
			offer_type=Order.OFFER_TYPE_BASIC,
			status=Order.STATUS_COMPLETED,
		)
		Order.objects.create(
			customer_user=self.auth_user,
			business_user=self.business_user,
			title='Completed 2',
			revisions=2,
			delivery_time_in_days=5,
			price='240.00',
			features=['Feature F'],
			offer_type=Order.OFFER_TYPE_STANDARD,
			status=Order.STATUS_COMPLETED,
		)
		Order.objects.create(
			customer_user=self.auth_user,
			business_user=self.business_user,
			title='In Progress Ignored',
			revisions=2,
			delivery_time_in_days=5,
			price='260.00',
			features=['Feature G'],
			offer_type=Order.OFFER_TYPE_PREMIUM,
			status=Order.STATUS_IN_PROGRESS,
		)
		Order.objects.create(
			customer_user=self.auth_user,
			business_user=self.other_business_user,
			title='Other Business Completed Ignored',
			revisions=2,
			delivery_time_in_days=5,
			price='280.00',
			features=['Feature H'],
			offer_type=Order.OFFER_TYPE_BASIC,
			status=Order.STATUS_COMPLETED,
		)

	def test_completed_order_count_requires_authentication(self):
		"""Anonymous requests must be rejected with HTTP 401."""
		response = self.client.get(
			f'/api/completed-order-count/{self.business_user.id}/'
		)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_completed_order_count_returns_correct_count(self):
		"""Endpoint must return only completed orders for target business user."""
		self.client.force_authenticate(user=self.auth_user)
		response = self.client.get(
			f'/api/completed-order-count/{self.business_user.id}/'
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data, {'completed_order_count': 2})

	def test_completed_order_count_returns_404_for_unknown_business_user(self):
		"""Unknown business user id must return HTTP 404."""
		self.client.force_authenticate(user=self.auth_user)
		response = self.client.get('/api/completed-order-count/999999/')

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
