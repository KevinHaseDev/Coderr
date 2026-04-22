"""Tests for review API endpoints."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from profiles_app.models import Profile
from reviews_app.models import Review

User = get_user_model()


class ReviewListApiTests(APITestCase):
	"""Validate GET /api/reviews/ behavior."""

	LIST_URL = '/api/reviews/'

	def setUp(self):
		"""Set up test data with multiple reviews and users for filtering and ordering tests."""
		self.auth_user = self._create_user('auth_user')
		self.business_user = self._create_user('business_user')
		self.other_business_user = self._create_user('other_business_user')
		self.reviewer_one = self._create_user('reviewer_one')
		self.reviewer_two = self._create_user('reviewer_two')

		self.review_one = Review.objects.create(
			business_user=self.business_user,
			reviewer=self.reviewer_one,
			rating=2,
			description='Review one',
		)
		self.review_two = Review.objects.create(
			business_user=self.business_user,
			reviewer=self.reviewer_two,
			rating=5,
			description='Review two',
		)
		self.review_three = Review.objects.create(
			business_user=self.other_business_user,
			reviewer=self.reviewer_one,
			rating=4,
			description='Review three',
		)

		now = timezone.now()
		Review.objects.filter(pk=self.review_one.pk).update(
			updated_at=now - timedelta(days=2),
		)
		Review.objects.filter(pk=self.review_two.pk).update(
			updated_at=now - timedelta(days=1),
		)
		Review.objects.filter(pk=self.review_three.pk).update(updated_at=now)

		self.review_one.refresh_from_db()
		self.review_two.refresh_from_db()
		self.review_three.refresh_from_db()

	def _create_user(self, username):
		"""Helper method to create a user with a profile for testing."""
		return User.objects.create_user(
			username=username,
			email=f'{username}@example.com',
			password='StrongPass123',
		)

	def test_get_reviews_requires_authentication(self):
		"""Anonymous requests must be rejected with HTTP 401."""
		response = self.client.get(self.LIST_URL)
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_get_reviews_returns_list_for_authenticated_user(self):
		"""Authenticated users should receive a list of reviews."""
		self.client.force_authenticate(user=self.auth_user)
		response = self.client.get(self.LIST_URL)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 3)
		returned_ids = {item['id'] for item in response.data}
		self.assertSetEqual(
			returned_ids,
			{self.review_one.id, self.review_two.id, self.review_three.id},
		)

	def test_get_reviews_filters_by_business_user_id(self):
		"""Filter reviews by business_user_id."""
		self.client.force_authenticate(user=self.auth_user)
		response = self.client.get(
			self.LIST_URL,
			{'business_user_id': self.business_user.id},
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 2)
		returned_ids = {item['id'] for item in response.data}
		self.assertSetEqual(returned_ids, {self.review_one.id, self.review_two.id})

	def test_get_reviews_filters_by_reviewer_id(self):
		"""Filter reviews by reviewer_id."""
		self.client.force_authenticate(user=self.auth_user)
		response = self.client.get(
			self.LIST_URL,
			{'reviewer_id': self.reviewer_one.id},
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 2)
		returned_ids = {item['id'] for item in response.data}
		self.assertSetEqual(returned_ids, {self.review_one.id, self.review_three.id})

	def test_get_reviews_supports_ordering_by_updated_at(self):
		"""Order reviews by updated_at."""
		self.client.force_authenticate(user=self.auth_user)
		response = self.client.get(self.LIST_URL, {'ordering': 'updated_at'})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		returned_ids = [item['id'] for item in response.data]
		self.assertEqual(
			returned_ids,
			[self.review_one.id, self.review_two.id, self.review_three.id],
		)

	def test_get_reviews_supports_ordering_by_rating(self):
		"""Order reviews by rating."""
		self.client.force_authenticate(user=self.auth_user)
		response = self.client.get(self.LIST_URL, {'ordering': 'rating'})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		returned_ids = [item['id'] for item in response.data]
		self.assertEqual(
			returned_ids,
			[self.review_one.id, self.review_three.id, self.review_two.id],
		)

	def test_get_reviews_returns_400_for_invalid_ordering(self):
		"""Return HTTP 400 for invalid ordering parameter."""
		self.client.force_authenticate(user=self.auth_user)
		response = self.client.get(self.LIST_URL, {'ordering': 'created_at'})

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('ordering', response.data)


class ReviewCreateApiTests(APITestCase):
	"""Validate POST /api/reviews/ behavior."""

	LIST_URL = '/api/reviews/'

	def setUp(self):
		"""Set up test data with users of different types for review creation tests."""
		self.customer_user = self._create_user_with_profile(
			'customer_user',
			Profile.TYPE_CUSTOMER,
		)
		self.business_user = self._create_user_with_profile(
			'business_user_for_reviews',
			Profile.TYPE_BUSINESS,
		)
		self.non_customer_user = self._create_user_with_profile(
			'non_customer_user',
			Profile.TYPE_BUSINESS,
		)
		self.customer_as_business_target = self._create_user_with_profile(
			'customer_target_user',
			Profile.TYPE_CUSTOMER,
		)

	def _create_user_with_profile(self, username, user_type):
		"""Helper method to create a user with a profile for testing."""
		user = User.objects.create_user(
			username=username,
			email=f'{username}@example.com',
			password='StrongPass123',
		)
		Profile.objects.create(user=user, user_type=user_type)
		return user

	def test_post_review_requires_authentication(self):
		"""Anonymous users must be rejected with HTTP 401 when creating a review."""
		payload = {
			'business_user': self.business_user.id,
			'rating': 4,
			'description': 'Alles war toll!',
		}
		response = self.client.post(self.LIST_URL, payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_post_review_allows_only_customer_users(self):
		"""Only users with customer profiles should be able to create reviews."""
		self.client.force_authenticate(user=self.non_customer_user)
		payload = {
			'business_user': self.business_user.id,
			'rating': 4,
			'description': 'Business user should be rejected.',
		}
		response = self.client.post(self.LIST_URL, payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_post_review_sets_reviewer_automatically(self):
		"""The reviewer should be set to the authenticated user regardless of input."""
		self.client.force_authenticate(user=self.customer_user)
		payload = {
			'business_user': self.business_user.id,
			'reviewer': self.non_customer_user.id,
			'rating': 5,
			'description': 'Automatisch gesetzter Reviewer.',
		}
		response = self.client.post(self.LIST_URL, payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		review = Review.objects.get(id=response.data['id'])
		self.assertEqual(review.reviewer_id, self.customer_user.id)
		self.assertEqual(response.data['reviewer'], self.customer_user.id)

	def test_post_review_forbids_duplicate_reviewer_business_user_combination(self):
		"""A reviewer should not be able to create more than one review for the same business user."""
		Review.objects.create(
			business_user=self.business_user,
			reviewer=self.customer_user,
			rating=4,
			description='Bereits vorhanden',
		)
		self.client.force_authenticate(user=self.customer_user)
		payload = {
			'business_user': self.business_user.id,
			'rating': 3,
			'description': 'Doppelte Bewertung',
		}
		response = self.client.post(self.LIST_URL, payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('non_field_errors', response.data)

	def test_post_review_returns_400_for_invalid_business_user_type(self):
		"""Return HTTP 400 when the business_user has an invalid type."""
		self.client.force_authenticate(user=self.customer_user)
		payload = {
			'business_user': self.customer_as_business_target.id,
			'rating': 4,
			'description': 'Ungültiger business_user Typ',
		}
		response = self.client.post(self.LIST_URL, payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('business_user', response.data)


class ReviewPatchDeleteApiTests(APITestCase):
	"""Validate PATCH and DELETE /api/reviews/{id}/ behavior."""

	def setUp(self):
		"""Set up test data with a review and users for testing update and delete permissions."""
		self.owner_user = self._create_user_with_profile(
			'owner_user',
			Profile.TYPE_CUSTOMER,
		)
		self.other_user = self._create_user_with_profile(
			'other_user',
			Profile.TYPE_CUSTOMER,
		)
		self.business_user = self._create_user_with_profile(
			'business_user_for_patch_delete',
			Profile.TYPE_BUSINESS,
		)
		self.review = Review.objects.create(
			business_user=self.business_user,
			reviewer=self.owner_user,
			rating=3,
			description='Initial review text',
		)
		self.url = f'/api/reviews/{self.review.id}/'

	def _create_user_with_profile(self, username, user_type):
		"""Helper method to create a user with a profile for testing."""
		user = User.objects.create_user(
			username=username,
			email=f'{username}@example.com',
			password='StrongPass123',
		)
		Profile.objects.create(user=user, user_type=user_type)
		return user

	def test_patch_review_requires_authentication(self):
		"""Anonymous users must be rejected with HTTP 401 when updating a review."""
		response = self.client.patch(
			self.url,
			{'rating': 5, 'description': 'Updated text'},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_patch_review_is_forbidden_for_non_owner(self):
		"""Only the owner of the review should be able to update it."""
		self.client.force_authenticate(user=self.other_user)
		response = self.client.patch(
			self.url,
			{'rating': 5, 'description': 'Not allowed update'},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_patch_review_returns_404_for_unknown_id(self):
		"""Return HTTP 404 when trying to update a non-existent review."""
		self.client.force_authenticate(user=self.owner_user)
		response = self.client.patch(
			'/api/reviews/999999/',
			{'rating': 5, 'description': 'Missing review'},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_patch_review_updates_rating_and_description(self):
		"""Update the rating and description of a review."""
		self.client.force_authenticate(user=self.owner_user)
		payload = {'rating': 5, 'description': 'Jetzt deutlich besser'}
		response = self.client.patch(self.url, payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.review.refresh_from_db()
		self.assertEqual(self.review.rating, 5)
		self.assertEqual(self.review.description, 'Jetzt deutlich besser')
		self.assertEqual(response.data['rating'], 5)
		self.assertEqual(response.data['description'], 'Jetzt deutlich besser')

	def test_delete_review_requires_authentication(self):
		"""Anonymous users must be rejected with HTTP 401 when deleting a review."""
		response = self.client.delete(self.url)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_delete_review_is_forbidden_for_non_owner(self):
		"""Only the owner of the review should be able to delete it."""
		self.client.force_authenticate(user=self.other_user)
		response = self.client.delete(self.url)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_delete_review_returns_404_for_unknown_id(self):
		"""Return HTTP 404 when trying to delete a non-existent review."""
		self.client.force_authenticate(user=self.owner_user)
		response = self.client.delete('/api/reviews/999999/')

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_delete_review_returns_204_and_removes_object(self):
		"""Delete a review and ensure it is removed from the database."""
		self.client.force_authenticate(user=self.owner_user)
		response = self.client.delete(self.url)

		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())
