"""Главная страница и обработчик ошибки 404."""
from typing import Optional

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница: описание приложения и переходы по разделам."""
    return render(request, "homepage/index.html")


def page_not_found(
    request: HttpRequest,
    exception: Optional[Exception] = None,
) -> HttpResponse:
    """Собственный обработчик 404 (handler404) для несуществующих URL."""
    return render(request, "404.html", status=404)
