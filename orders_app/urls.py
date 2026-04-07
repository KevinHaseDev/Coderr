from django.urls import include, path

urlpatterns = [
    path('', include('orders_app.api.urls')),
]
