"""Tests for the info_app base-info endpoint."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer
from profiles_app.models import Profile
from reviews_app.models import Review

User = get_user_model()


class BaseInfoApiTests(APITestCase):
    """Validate GET /api/base-info/ aggregation behavior."""

    URL = '/api/base-info/'

    def _create_user_with_profile(self, username, user_type):
        """Helper to create a user with a profile of the specified type."""
        user = User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='StrongPass123',
        )
        Profile.objects.create(user=user, user_type=user_type)
        return user

    def test_base_info_is_public(self):
        """Test that the base info endpoint is accessible without authentication."""
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_base_info_returns_aggregated_counts(self):
        """Test that the base info endpoint returns correct aggregated counts and average rating."""
        business_one = self._create_user_with_profile(
            'business_one',
            Profile.TYPE_BUSINESS,
        )
        business_two = self._create_user_with_profile(
            'business_two',
            Profile.TYPE_BUSINESS,
        )
        reviewer_one = self._create_user_with_profile(
            'reviewer_one',
            Profile.TYPE_CUSTOMER,
        )
        reviewer_two = self._create_user_with_profile(
            'reviewer_two',
            Profile.TYPE_CUSTOMER,
        )

        Offer.objects.create(
            user=business_one,
            title='Offer 1',
            description='Desc 1',
            image=None,
        )
        Offer.objects.create(
            user=business_two,
            title='Offer 2',
            description='Desc 2',
            image=None,
        )

        Review.objects.create(
            business_user=business_one,
            reviewer=reviewer_one,
            rating=4,
            description='Great',
        )
        Review.objects.create(
            business_user=business_two,
            reviewer=reviewer_two,
            rating=5,
            description='Excellent',
        )

        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['review_count'], 2)
        self.assertEqual(response.data['average_rating'], 4.5)
        self.assertEqual(response.data['business_profile_count'], 2)
        self.assertEqual(response.data['offer_count'], 2)

    def test_base_info_returns_zero_average_without_reviews(self):
        """Test that the average rating is returned as 0.0 when there are no reviews."""
        self._create_user_with_profile('business_only', Profile.TYPE_BUSINESS)

        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['review_count'], 0)
        self.assertEqual(response.data['average_rating'], 0.0)
