from django.urls import path

from orders_app.api.views import OrderListCreateView


urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list-create'),
]
