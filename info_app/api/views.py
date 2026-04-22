from django.db.models import Avg
from rest_framework import generics, permissions
from rest_framework.response import Response

from offers_app.models import Offer
from profiles_app.models import Profile
from reviews_app.models import Review


class BaseInfoView(generics.GenericAPIView):
    """Return aggregated platform base information."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Return aggregated platform information including review count, average rating, business profile count, and offer count."""
        average_rating = Review.objects.aggregate(value=Avg('rating'))['value']
        rounded_average_rating = 0.0 if average_rating is None else round(float(average_rating), 1)
        return Response(
            {
                'review_count': Review.objects.count(),
                'average_rating': rounded_average_rating,
                'business_profile_count': Profile.objects.filter(
                    user_type=Profile.TYPE_BUSINESS,
                ).count(),
                'offer_count': Offer.objects.count(),
            }
        )
