from rest_framework import generics, permissions
from rest_framework.response import Response


class ReviewsAppStatusView(generics.GenericAPIView):
	"""Temporary placeholder endpoint until review features are implemented."""

	permission_classes = [permissions.AllowAny]

	def get(self, request):
		return Response({'detail': 'Reviews API placeholder endpoint.'})
