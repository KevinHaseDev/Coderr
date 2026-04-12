from django.urls import path

from orders_app.api.views import OrderListCreateView, OrderUpdateDeleteView


urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list-create'),
    path('<int:pk>/', OrderUpdateDeleteView.as_view(), name='order-update-delete'),
]
