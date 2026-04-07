from django.urls import include, path

urlpatterns = [
    path('', include('offers_app.api.urls')),
]
