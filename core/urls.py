from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('auth_app.urls')),
    path('api/', include('profiles_app.urls')),
    path('api/', include('offers_app.urls')),
    path('api/orders/', include('orders_app.urls')),
    path('api/reviews/', include('reviews_app.urls')),
]
