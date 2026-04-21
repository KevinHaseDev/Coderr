from django.urls import path

from reviews_app.api.views import ReviewUpdateDeleteView, ReviewsAppStatusView

urlpatterns = [
	path('', ReviewsAppStatusView.as_view(), name='review-list-create'),
	path('<int:pk>/', ReviewUpdateDeleteView.as_view(), name='review-detail'),
]
