"""Фильтры шаблонов Maestro."""
from typing import Optional

from django import template

from models.albums import get_rating_stars

register = template.Library()


@register.filter(name="stars")
def stars(rating: Optional[int]) -> str:
    """Оценка 1–5 в виде звёзд; для None (нет оценки) — пустые звёзды."""
    return get_rating_stars(rating)
