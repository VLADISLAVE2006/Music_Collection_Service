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


def not_found(
    title: str,
    back_url: str,
    back_text: str,
    message: str = "",
) -> HttpResponse:
    """Страница с сообщением об ошибке и кодом ответа 404."""
    text = f'<p class="lead">{escape(message)}</p>' if message else ""
    content = f"""
    <p class="display-1 text-danger fw-bold">404</p>
    <h1>{escape(title)}</h1>
    {text}
    <a href="{back_url}" class="btn btn-outline-secondary">
        ← {escape(back_text)}
    </a>
    """
    return HttpResponse(page(title, content), status=404)


def page_not_found(
    request: HttpRequest,
    exception: Exception | None = None,
) -> HttpResponse:
    """Собственный обработчик 404 (handler404) для несуществующих URL."""
    return not_found(
        "Страница не найдена",
        "/",
        "на главную",
        "Такого адреса нет. Проверьте ссылку или вернитесь на главную.",
    )


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
