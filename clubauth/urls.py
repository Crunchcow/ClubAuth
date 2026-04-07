from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("users.urls")),
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path("social-auth/", include("social_django.urls", namespace="social")),
]
