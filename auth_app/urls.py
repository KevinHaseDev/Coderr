from django.urls import include, path

urlpatterns = [
    path('', include('auth_app.api.urls')),
]