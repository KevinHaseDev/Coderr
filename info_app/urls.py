from django.urls import include, path

urlpatterns = [
    path('', include('info_app.api.urls')),
]
