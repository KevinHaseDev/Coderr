from django.urls import path

from offers_app.api.views import OfferListView, OfferRetrieveView, OfferDetailRetrieveView


urlpatterns = [
    path('offers/', OfferListView.as_view(), name='offer-list'),
    path('offers/<int:pk>/', OfferRetrieveView.as_view(), name='offer-detail'),
    path('offerdetails/<int:pk>/', OfferDetailRetrieveView.as_view(), name='offerdetail-detail'),
]
