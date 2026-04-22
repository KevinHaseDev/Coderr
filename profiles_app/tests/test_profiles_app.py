from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from profiles_app.models import Profile


class ProfileDetailApiTests(APITestCase):
    """Validate profile detail retrieve and patch endpoint behavior."""

    def setUp(self):
        """Set up test data with two users and their profiles."""
        self.user = User.objects.create_user(
            username='max_mustermann',
            email='max@example.com',
            password='StrongPass123',
        )
        self.other_user = User.objects.create_user(
            username='anna_kunde',
            email='anna@example.com',
            password='StrongPass123',
        )
        Profile.objects.create(user=self.user, user_type=Profile.TYPE_BUSINESS)
        Profile.objects.create(
            user=self.other_user,
            user_type=Profile.TYPE_CUSTOMER,
        )
        self.url = reverse('profile-detail', kwargs={'pk': self.user.id})
        self.other_url = reverse('profile-detail', kwargs={'pk': self.other_user.id})
        self.missing_url = reverse('profile-detail', kwargs={'pk': 99999})

    def assert_required_text_fields_not_null(self, data):
        """Validate non-null contract for selected profile text fields."""
        fields = [
            'first_name',
            'last_name',
            'location',
            'tel',
            'description',
            'working_hours',
        ]
        for field in fields:
            self.assertIsNotNone(data[field])

    def test_get_requires_authentication(self):
        """Anonymous requests must be rejected with HTTP 401."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_returns_empty_strings_for_required_text_fields(self):
        """Selected response fields must never be null in API output."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_required_text_fields_not_null(response.data)
        self.assertEqual(response.data['first_name'], '')
        self.assertEqual(response.data['last_name'], '')
        self.assertEqual(response.data['location'], '')
        self.assertEqual(response.data['tel'], '')
        self.assertEqual(response.data['description'], '')
        self.assertEqual(response.data['working_hours'], '')

    def test_patch_requires_authentication(self):
        """Anonymous PATCH requests must be rejected with HTTP 401."""
        response = self.client.patch(self.url, {'location': 'Berlin'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_forbidden_for_non_owner(self):
        """Authenticated users must not update a foreign profile."""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            self.other_url,
            {'description': 'Not allowed'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_returns_404_if_profile_does_not_exist(self):
        """Updating a profile for a missing user id must return HTTP 404."""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            self.missing_url,
            {'location': 'Berlin'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_updates_profile_and_user_fields(self):
        """PATCH should update mapped profile and user fields."""
        payload = {
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'location': 'Berlin',
            'tel': '123456789',
            'description': 'Business description',
            'working_hours': '9-17',
            'email': 'new_email@business.de',
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, payload, format='json')
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assert_required_text_fields_not_null(response.data)
        self.assertEqual(self.user.first_name, 'Max')
        self.assertEqual(self.user.email, 'new_email@business.de')
        self.assertEqual(response.data['working_hours'], '9-17')
        self.assertEqual(response.data['email'], 'new_email@business.de')
