"""Главная страница и общий каркас HTML-страниц проекта."""
from html import escape

from django.http import HttpRequest, HttpResponse

BOOTSTRAP_CSS = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
    "/dist/css/bootstrap.min.css"
)


def page(title: str, content: str) -> str:
    """Собрать HTML-документ: кодировка, Bootstrap, навигация, содержимое."""
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(title)}</title>
    <link rel="stylesheet" href="{BOOTSTRAP_CSS}">
</head>
<body>
    <nav class="nav border-bottom mb-4">
        <a class="nav-link" href="/">Главная</a>
        <a class="nav-link" href="/albums/">Альбомы</a>
        <a class="nav-link" href="/artists/">Исполнители</a>
        <a class="nav-link" href="/collections/">Коллекции</a>
    </nav>
    <main class="container">{content}</main>
</body>
</html>"""


def not_found(title: str, back_url: str, back_text: str) -> HttpResponse:
    """Страница с сообщением об ошибке и кодом ответа 404."""
    content = f"""
    <h1 class="text-danger">{escape(title)}</h1>
    <a href="{back_url}" class="btn btn-outline-secondary">
        ← {escape(back_text)}
    </a>
    """
    return HttpResponse(page(title, content), status=404)


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница: описание приложения и переходы по разделам."""
    content = """
    <h1 class="display-4">Maestro</h1>
    <p class="lead">Сервис музыкальных коллекций.</p>
    <p>Основные разделы:</p>
    <a href="/albums/" class="btn btn-primary me-2">Альбомы</a>
    <a href="/artists/" class="btn btn-secondary me-2">Исполнители</a>
    <a href="/collections/" class="btn btn-success">Коллекции</a>
    """
    return HttpResponse(page("Maestro", content))
