"""Маршруты приложения альбомов."""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.albums, name="albums"),
    path("<int:album_id>/", views.album_detail, name="album_detail"),
]
