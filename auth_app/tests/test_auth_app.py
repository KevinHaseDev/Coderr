"""Tests for auth API registration and login endpoints."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from profiles_app.models import Profile

User = get_user_model()


class RegistrationApiTests(APITestCase):
	"""Validate registration endpoint behavior."""

	URL = '/api/registration/'

	def test_registration_creates_user_profile_and_token(self):
		payload = {
			'username': 'new_customer',
			'email': 'new_customer@example.com',
			'password': 'StrongPass123',
			'repeated_password': 'StrongPass123',
			'type': Profile.TYPE_CUSTOMER,
		}
		response = self.client.post(self.URL, payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(Token.objects.filter(key=response.data['token']).exists())
		created_user = User.objects.get(username='new_customer')
		self.assertEqual(response.data['user_id'], created_user.id)
		self.assertEqual(created_user.profile.user_type, Profile.TYPE_CUSTOMER)

	def test_registration_rejects_duplicate_username(self):
		User.objects.create_user(
			username='existing_user',
			email='old@example.com',
			password='StrongPass123',
		)
		payload = {
			'username': 'existing_user',
			'email': 'new@example.com',
			'password': 'StrongPass123',
			'repeated_password': 'StrongPass123',
			'type': Profile.TYPE_BUSINESS,
		}
		response = self.client.post(self.URL, payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('username', response.data)

	def test_registration_rejects_password_mismatch(self):
		payload = {
			'username': 'mismatch_user',
			'email': 'mismatch@example.com',
			'password': 'StrongPass123',
			'repeated_password': 'DifferentPass123',
			'type': Profile.TYPE_CUSTOMER,
		}
		response = self.client.post(self.URL, payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('repeated_password', response.data)


class LoginApiTests(APITestCase):
	"""Validate login endpoint behavior."""

	URL = '/api/login/'

	def setUp(self):
		self.user = User.objects.create_user(
			username='login_user',
			email='login_user@example.com',
			password='StrongPass123',
		)

	def test_login_returns_token_for_valid_credentials(self):
		response = self.client.post(
			self.URL,
			{'username': 'login_user', 'password': 'StrongPass123'},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(Token.objects.filter(user=self.user).exists())
		self.assertEqual(response.data['username'], self.user.username)

	def test_login_rejects_invalid_credentials(self):
		response = self.client.post(
			self.URL,
			{'username': 'login_user', 'password': 'WrongPassword'},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(response.data, {'detail': 'Invalid credentials.'})
