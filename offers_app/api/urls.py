from django.urls import path

from offers_app.api.views import OfferListView, OfferRetrieveView


urlpatterns = [
    path('', OfferListView.as_view(), name='offer-list'),
    path('<int:pk>/', OfferRetrieveView.as_view(), name='offer-detail'),
]
