"""Tests for review API endpoints."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from reviews_app.models import Review

User = get_user_model()


class ReviewListApiTests(APITestCase):
	"""Validate GET /api/reviews/ behavior."""

	LIST_URL = '/api/reviews/'

	def setUp(self):
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
		return User.objects.create_user(
			username=username,
			email=f'{username}@example.com',
			password='StrongPass123',
		)

	def test_get_reviews_requires_authentication(self):
		response = self.client.get(self.LIST_URL)
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_get_reviews_returns_list_for_authenticated_user(self):
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
		self.client.force_authenticate(user=self.auth_user)
		response = self.client.get(self.LIST_URL, {'ordering': 'updated_at'})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		returned_ids = [item['id'] for item in response.data]
		self.assertEqual(
			returned_ids,
			[self.review_one.id, self.review_two.id, self.review_three.id],
		)

	def test_get_reviews_supports_ordering_by_rating(self):
		self.client.force_authenticate(user=self.auth_user)
		response = self.client.get(self.LIST_URL, {'ordering': 'rating'})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		returned_ids = [item['id'] for item in response.data]
		self.assertEqual(
			returned_ids,
			[self.review_one.id, self.review_three.id, self.review_two.id],
		)

	def test_get_reviews_returns_400_for_invalid_ordering(self):
		self.client.force_authenticate(user=self.auth_user)
		response = self.client.get(self.LIST_URL, {'ordering': 'created_at'})

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('ordering', response.data)
