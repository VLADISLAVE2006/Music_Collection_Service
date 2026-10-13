"""Маршруты приложения коллекций."""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.collections, name="collections"),
    path(
        "<int:collection_id>/",
        views.collection_detail,
        name="collection_detail",
    ),
]
