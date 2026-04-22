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


class ProfileListApiTests(APITestCase):
    """Validate business and customer profile list endpoint behavior."""

    def setUp(self):
        """Create fixture users and profiles for both list endpoints."""
        self.business_user = User.objects.create_user(
            username='business_one',
            email='business_one@example.com',
            password='StrongPass123',
        )
        self.business_user.first_name = 'Berta'
        self.business_user.last_name = 'Business'
        self.business_user.save()
        self.customer_user = User.objects.create_user(
            username='customer_one',
            email='customer_one@example.com',
            password='StrongPass123',
        )
        self.customer_user.first_name = 'Clara'
        self.customer_user.last_name = 'Customer'
        self.customer_user.save()
        self.request_user = User.objects.create_user(
            username='viewer',
            email='viewer@example.com',
            password='StrongPass123',
        )
        Profile.objects.create(
            user=self.business_user,
            user_type=Profile.TYPE_BUSINESS,
            location='Berlin',
            telephone='123456789',
            description='Business profile',
            working_hours='9-17',
        )
        Profile.objects.create(
            user=self.customer_user,
            user_type=Profile.TYPE_CUSTOMER,
        )
        Profile.objects.create(
            user=self.request_user,
            user_type=Profile.TYPE_BUSINESS,
        )
        self.business_list_url = reverse('business-profile-list')
        self.customer_list_url = reverse('customer-profile-list')

    def test_business_list_requires_authentication(self):
        """Anonymous requests must be rejected for business list endpoint."""
        response = self.client.get(self.business_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_list_requires_authentication(self):
        """Anonymous requests must be rejected for customer list endpoint."""
        response = self.client.get(self.customer_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_business_list_returns_array_with_business_profiles_only(self):
        """Business list should return a JSON array filtered by business type."""
        self.client.force_authenticate(user=self.request_user)
        response = self.client.get(self.business_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)
        self.assertTrue(all(item['type'] == Profile.TYPE_BUSINESS for item in response.data))
        first_item = response.data[0]
        self.assertIn('location', first_item)
        self.assertIn('tel', first_item)
        self.assertIn('description', first_item)
        self.assertIn('working_hours', first_item)

    def test_customer_list_returns_array_with_customer_profiles_only(self):
        """Customer list should return a JSON array filtered by customer type."""
        self.client.force_authenticate(user=self.request_user)
        response = self.client.get(self.customer_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        profile = response.data[0]
        self.assertEqual(profile['username'], 'customer_one')
        self.assertEqual(profile['type'], Profile.TYPE_CUSTOMER)
        self.assertIn('uploaded_at', profile)
