"""Маршруты приложения альбомов."""
from django.urls import path

from . import views

app_name = "albums"

urlpatterns = [
    path("", views.albums, name="list"),
    path("<int:album_id>/", views.album_detail, name="detail"),
]
