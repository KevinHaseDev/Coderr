from django.urls import path

from orders_app.api.views import (
    OrderCountView,
    OrderListCreateView,
    OrderUpdateDeleteView,
)


urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderUpdateDeleteView.as_view(), name='order-update-delete'),
    path('order-count/<int:business_user_id>/', OrderCountView.as_view(), name='order-count'),
]
