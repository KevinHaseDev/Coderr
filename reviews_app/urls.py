from django.urls import include, path

urlpatterns = [
    path('', include('reviews_app.api.urls')),
]
