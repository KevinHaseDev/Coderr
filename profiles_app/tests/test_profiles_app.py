from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from profiles_app.models import Profile


class ProfileDetailApiTests(APITestCase):
    """Validate profile detail retrieve and patch endpoint behavior."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='max_mustermann',
            email='max@example.com',
            password='StrongPass123',
        )
        Profile.objects.create(user=self.user, user_type=Profile.TYPE_BUSINESS)
        self.url = reverse('profile-detail', kwargs={'pk': self.user.id})

    def test_get_requires_authentication(self):
        """Anonymous requests must be rejected with HTTP 401."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_returns_empty_strings_for_required_text_fields(self):
        """Selected response fields must never be null in API output."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        fields = ['first_name', 'last_name', 'location']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in fields:
            self.assertEqual(response.data[field], '')
        self.assertEqual(response.data['tel'], '')
        self.assertEqual(response.data['description'], '')
        self.assertEqual(response.data['working_hours'], '')

    def test_patch_updates_profile_and_user_fields(self):
        """PATCH should update mapped profile and user fields."""
        payload = {
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'location': 'Berlin',
            'tel': '123456789',
            'description': 'Business description',
            'working_hours': '9-17',
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, payload, format='json')
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, 'Max')
        self.assertEqual(response.data['working_hours'], '9-17')
