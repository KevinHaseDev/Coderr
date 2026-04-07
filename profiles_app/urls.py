from django.urls import include, path

urlpatterns = [
    path('', include('profiles_app.api.urls')),
]
