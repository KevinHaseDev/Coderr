from django.urls import path

from offers_app.api.views import OfferListView, OfferRetrieveView, OfferDetailRetrieveView


urlpatterns = [
    path('', OfferListView.as_view(), name='offer-list'),
    path('<int:pk>/', OfferRetrieveView.as_view(), name='offer-detail'),
    path('<int:pk>/', OfferDetailRetrieveView.as_view(), name='offerdetail-detail'),
]
