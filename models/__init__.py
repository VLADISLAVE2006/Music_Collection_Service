"""Пакет с классами предметной области."""
from .artists import Artist
from .users import User
from .albums import Album
from .collection import Collection

__all__ = ["Artist", "User", "Album", "Collection"]
