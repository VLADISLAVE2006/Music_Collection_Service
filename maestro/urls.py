"""Корневая маршрутизация проекта Maestro."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("albums/", include("albums.urls")),
    path("artists/", include("artists.urls")),
    path("collections/", include("library.urls")),
]
