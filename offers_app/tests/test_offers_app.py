"""Tests for the offers API endpoints."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from profiles_app.models import Profile

User = get_user_model()


@override_settings(ROOT_URLCONF='offers_app.tests_urls')
class OfferApiTestBase(APITestCase):
	"""Shared fixtures and helpers for offer endpoint tests."""

	LIST_URL = '/api/offers/'

	def setUp(self):
		self.owner = self._create_user('owner_business', Profile.TYPE_BUSINESS)
		self.other_business = self._create_user(
			'other_business',
			Profile.TYPE_BUSINESS,
		)
		self.customer = self._create_user('customer_user', Profile.TYPE_CUSTOMER)

	def _create_user(self, username, user_type):
		user = User.objects.create_user(
			username=username,
			email=f'{username}@example.com',
			password='StrongPass123',
		)
		Profile.objects.create(user=user, user_type=user_type)
		return user

	def _create_offer(
		self,
		user,
		title='Service Offer',
		description='Default description',
		prices=(100, 200, 300),
		delivery_days=(5, 7, 10),
	):
		offer = Offer.objects.create(
			user=user,
			title=title,
			description=description,
			image=None,
		)
		offer_types = (
			OfferDetail.OFFER_TYPE_BASIC,
			OfferDetail.OFFER_TYPE_STANDARD,
			OfferDetail.OFFER_TYPE_PREMIUM,
		)
		labels = ('Basic', 'Standard', 'Premium')
		for offer_type, label, price, days in zip(
			offer_types,
			labels,
			prices,
			delivery_days,
		):
			OfferDetail.objects.create(
				offer=offer,
				title=f'{title} {label}',
				revisions=2,
				delivery_time_in_days=days,
				price=price,
				features=[f'{label} feature'],
				offer_type=offer_type,
			)
		return offer

	def _valid_offer_payload(self, title='New Offer'):
		return {
			'title': title,
			'image': None,
			'description': 'Created from tests',
			'details': [
				{
					'title': 'Basic Package',
					'revisions': 2,
					'delivery_time_in_days': 5,
					'price': 100,
					'features': ['Feature A'],
					'offer_type': OfferDetail.OFFER_TYPE_BASIC,
				},
				{
					'title': 'Standard Package',
					'revisions': 5,
					'delivery_time_in_days': 7,
					'price': 200,
					'features': ['Feature B'],
					'offer_type': OfferDetail.OFFER_TYPE_STANDARD,
				},
				{
					'title': 'Premium Package',
					'revisions': 10,
					'delivery_time_in_days': 10,
					'price': 300,
					'features': ['Feature C'],
					'offer_type': OfferDetail.OFFER_TYPE_PREMIUM,
				},
			],
		}


class OfferListApiTests(OfferApiTestBase):
	"""Tests for GET /api/offers/ list behavior."""

	def test_get_offers_is_public(self):
		self._create_offer(self.owner, title='Public Offer')
		response = self.client.get(self.LIST_URL)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['count'], 1)

	def test_get_offers_uses_pagination(self):
		for index in range(7):
			self._create_offer(self.owner, title=f'Offer {index}')
		response = self.client.get(self.LIST_URL)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['count'], 7)
		self.assertEqual(len(response.data['results']), 6)
		self.assertIsNotNone(response.data['next'])

	def test_get_offers_supports_page_size_parameter(self):
		for index in range(5):
			self._create_offer(self.owner, title=f'Page Offer {index}')
		response = self.client.get(self.LIST_URL, {'page_size': 2})
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data['results']), 2)

	def test_get_offers_filters_by_creator_id(self):
		owner_offer = self._create_offer(self.owner, title='Owner Offer')
		self._create_offer(self.other_business, title='Other Offer')
		response = self.client.get(self.LIST_URL, {'creator_id': self.owner.id})
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['count'], 1)
		self.assertEqual(response.data['results'][0]['id'], owner_offer.id)

	def test_get_offers_filters_by_min_price(self):
		self._create_offer(
			self.owner,
			title='Low Price Offer',
			prices=(50, 60, 70),
		)
		high_offer = self._create_offer(
			self.owner,
			title='High Price Offer',
			prices=(120, 140, 160),
		)
		response = self.client.get(self.LIST_URL, {'min_price': 100})
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['count'], 1)
		self.assertEqual(response.data['results'][0]['id'], high_offer.id)

	def test_get_offers_filters_by_max_delivery_time(self):
		fast_offer = self._create_offer(
			self.owner,
			title='Fast Offer',
			delivery_days=(2, 3, 4),
		)
		self._create_offer(
			self.owner,
			title='Slow Offer',
			delivery_days=(7, 8, 9),
		)
		response = self.client.get(self.LIST_URL, {'max_delivery_time': 4})
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['count'], 1)
		self.assertEqual(response.data['results'][0]['id'], fast_offer.id)

	def test_get_offers_supports_ordering_by_min_price(self):
		high_offer = self._create_offer(self.owner, title='High', prices=(300, 350, 400))
		low_offer = self._create_offer(self.owner, title='Low', prices=(100, 150, 200))
		mid_offer = self._create_offer(self.owner, title='Mid', prices=(200, 250, 300))
		response = self.client.get(self.LIST_URL, {'ordering': 'min_price'})
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		ids = [item['id'] for item in response.data['results']]
		self.assertEqual(ids, [low_offer.id, mid_offer.id, high_offer.id])

	def test_get_offers_supports_search_in_title_and_description(self):
		self._create_offer(
			self.owner,
			title='Logo Design',
			description='Branding package',
		)
		seo_offer = self._create_offer(
			self.owner,
			title='Web Package',
			description='Advanced SEO service',
		)
		response = self.client.get(self.LIST_URL, {'search': 'seo'})
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['count'], 1)
		self.assertEqual(response.data['results'][0]['id'], seo_offer.id)


class OfferDetailReadApiTests(OfferApiTestBase):
	"""Tests for GET /api/offers/{id}/ and /api/offerdetails/{id}/."""

	def setUp(self):
		super().setUp()
		self.offer = self._create_offer(self.owner, title='Detail Offer')
		self.detail = self.offer.details.get(offer_type=OfferDetail.OFFER_TYPE_BASIC)
		self.offer_url = f'/api/offers/{self.offer.id}/'
		self.offerdetail_url = f'/api/offerdetails/{self.detail.id}/'

	def test_get_offer_detail_requires_authentication(self):
		response = self.client.get(self.offer_url)
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_get_offer_detail_returns_offer_data_with_detail_urls(self):
		self.client.force_authenticate(user=self.owner)
		response = self.client.get(self.offer_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['id'], self.offer.id)
		self.assertEqual(len(response.data['details']), 3)
		self.assertTrue(all('url' in item for item in response.data['details']))
		self.assertEqual(Decimal(str(response.data['min_price'])), Decimal('100'))
		self.assertEqual(response.data['min_delivery_time'], 5)

	def test_get_offer_detail_returns_404_for_unknown_offer(self):
		self.client.force_authenticate(user=self.owner)
		response = self.client.get('/api/offers/999999/')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_get_offerdetail_requires_authentication(self):
		response = self.client.get(self.offerdetail_url)
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_get_offerdetail_returns_full_payload(self):
		self.client.force_authenticate(user=self.owner)
		response = self.client.get(self.offerdetail_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['id'], self.detail.id)
		self.assertEqual(response.data['title'], self.detail.title)
		self.assertEqual(response.data['offer_type'], OfferDetail.OFFER_TYPE_BASIC)
		self.assertEqual(response.data['revisions'], self.detail.revisions)

	def test_get_offerdetail_returns_404_for_unknown_detail(self):
		self.client.force_authenticate(user=self.owner)
		response = self.client.get('/api/offerdetails/999999/')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OfferCreateApiTests(OfferApiTestBase):
	"""Tests for POST /api/offers/."""

	def test_post_offer_requires_authentication(self):
		payload = self._valid_offer_payload()
		response = self.client.post(self.LIST_URL, payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_post_offer_requires_business_profile(self):
		self.client.force_authenticate(user=self.customer)
		payload = self._valid_offer_payload()
		response = self.client.post(self.LIST_URL, payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_post_offer_creates_offer_with_three_details(self):
		self.client.force_authenticate(user=self.owner)
		payload = self._valid_offer_payload(title='Created Offer')
		response = self.client.post(self.LIST_URL, payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		offer = Offer.objects.get(title='Created Offer')
		self.assertEqual(offer.user, self.owner)
		self.assertEqual(offer.details.count(), 3)
		self.assertEqual(len(response.data['details']), 3)

	def test_post_offer_rejects_invalid_detail_count(self):
		self.client.force_authenticate(user=self.owner)
		payload = self._valid_offer_payload()
		payload['details'] = payload['details'][:2]
		response = self.client.post(self.LIST_URL, payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('details', response.data)

	def test_post_offer_rejects_duplicate_offer_type(self):
		self.client.force_authenticate(user=self.owner)
		payload = self._valid_offer_payload()
		payload['details'][1]['offer_type'] = OfferDetail.OFFER_TYPE_BASIC
		response = self.client.post(self.LIST_URL, payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('details', response.data)


class OfferPatchApiTests(OfferApiTestBase):
	"""Tests for PATCH /api/offers/{id}/."""

	def setUp(self):
		super().setUp()
		self.offer = self._create_offer(self.owner, title='Patch Offer')
		self.url = f'/api/offers/{self.offer.id}/'

	def test_patch_offer_requires_authentication(self):
		response = self.client.patch(self.url, {'title': 'Updated'}, format='json')
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_patch_offer_forbidden_for_non_owner(self):
		self.client.force_authenticate(user=self.other_business)
		response = self.client.patch(self.url, {'title': 'Updated'}, format='json')
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_patch_offer_updates_target_detail_by_offer_type(self):
		basic_detail = self.offer.details.get(offer_type=OfferDetail.OFFER_TYPE_BASIC)
		standard_detail = self.offer.details.get(offer_type=OfferDetail.OFFER_TYPE_STANDARD)
		self.client.force_authenticate(user=self.owner)
		payload = {
			'title': 'Updated Offer Title',
			'details': [
				{
					'offer_type': OfferDetail.OFFER_TYPE_BASIC,
					'price': 120,
					'revisions': 4,
				}
			],
		}
		response = self.client.patch(self.url, payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.offer.refresh_from_db()
		basic_detail.refresh_from_db()
		standard_detail.refresh_from_db()
		self.assertEqual(self.offer.title, 'Updated Offer Title')
		self.assertEqual(basic_detail.revisions, 4)
		self.assertEqual(basic_detail.price, Decimal('120'))
		self.assertEqual(standard_detail.price, Decimal('200'))

	def test_patch_offer_requires_offer_type_for_detail_updates(self):
		self.client.force_authenticate(user=self.owner)
		payload = {'details': [{'price': 120}]}
		response = self.client.patch(self.url, payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('details', response.data)


class OfferDeleteApiTests(OfferApiTestBase):
	"""Tests for DELETE /api/offers/{id}/."""

	def setUp(self):
		super().setUp()
		self.offer = self._create_offer(self.owner, title='Delete Offer')
		self.url = f'/api/offers/{self.offer.id}/'

	def test_delete_offer_requires_authentication(self):
		response = self.client.delete(self.url)
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_delete_offer_forbidden_for_non_owner(self):
		self.client.force_authenticate(user=self.other_business)
		response = self.client.delete(self.url)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_delete_offer_returns_204_and_removes_object(self):
		self.client.force_authenticate(user=self.owner)
		response = self.client.delete(self.url)
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(response.content, b'')
		self.assertFalse(Offer.objects.filter(id=self.offer.id).exists())
