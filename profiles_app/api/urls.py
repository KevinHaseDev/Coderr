from django.urls import path

from profiles_app.api.views import (
	BusinessProfileListView,
	CustomerProfileListView,
	ProfileDetailView,
)

urlpatterns = [
	path(
		'profiles/business/',
		BusinessProfileListView.as_view(),
		name='business-profile-list',
	),
	path(
		'profiles/customer/',
		CustomerProfileListView.as_view(),
		name='customer-profile-list',
	),
	path(
		'profile/<int:pk>/',
		ProfileDetailView.as_view(),
		name='profile-detail',
	),
]
