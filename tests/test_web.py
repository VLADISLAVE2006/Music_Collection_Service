import os
from datetime import date

import django
import pytest
from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from django.test import Client
from django.test.utils import setup_test_environment
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "maestro.settings")
django.setup()
try:
    setup_test_environment()
except RuntimeError:
    pass

from main import load_data  # noqa: E402
from models import Album, Artist, User  # noqa: E402

PAGES = {
    "/": "homepage/index.html",
    "/albums/": "albums/album_list.html",
    "/albums/1/": "albums/album_detail.html",
    "/artists/": "artists/artist_list.html",
    "/artists/1/": "artists/artist_detail.html",
    "/collections/": "library/collection_list.html",
    "/collections/1/": "library/collection_detail.html",
}

MISSING = {
    "/albums/999/": ("albums/album_detail.html", "Альбом не найден"),
    "/artists/999/": ("artists/artist_detail.html", "Исполнитель не найден"),
    "/collections/999/": (
        "library/collection_detail.html", "Коллекция не найдена",
    ),
}


@pytest.fixture
def client():
    return Client(HTTP_HOST="127.0.0.1")


def template_names(response):
    return [template.name for template in response.templates]


@pytest.mark.parametrize("url", PAGES)
def test_pages_return_200(client, url):
    response = client.get(url)
    assert response.status_code == 200
    assert "bootstrap" in response.content.decode("utf-8")


@pytest.mark.parametrize("url, template", PAGES.items())
def test_pages_use_templates(client, url, template):
    names = template_names(client.get(url))
    assert template in names
    assert "base.html" in names
    assert "includes/navigation.html" in names


@pytest.mark.parametrize("url", MISSING)
def test_missing_object_returns_404_from_template(client, url):
    template, message = MISSING[url]
    response = client.get(url)
    assert response.status_code == 404
    assert template in template_names(response)
    assert message in response.content.decode("utf-8")


def test_unknown_url_uses_custom_handler404(client):
    response = client.get("/nothing/")
    text = response.content.decode("utf-8")
    assert response.status_code == 404
    assert "404.html" in template_names(response)
    assert "Страница не найдена" in text


def test_handler404_is_registered():
    from maestro import urls
    assert urls.handler404 == "homepage.views.page_not_found"


def test_page_function_is_removed():
    from homepage import views
    assert not hasattr(views, "page")


def test_context_is_passed_to_template(client):
    response = client.get("/albums/")
    albums = load_data()[2]
    assert len(response.context["albums"]) == len(albums)
    detail = client.get("/albums/1/")
    assert detail.context["album"].id == 1
    assert detail.context["status"]


def test_album_page_shows_linked_objects(client):
    text = client.get("/albums/1/").content.decode("utf-8")
    assert "After Hours" in text
    assert "The Weeknd" in text
    assert reverse("artists:detail", args=[1]) in text


def test_collection_page_shows_statistics(client):
    text = client.get("/collections/1/").content.decode("utf-8")
    assert "Всего альбомов" in text
    assert "Средняя оценка" in text


def test_namespaced_urls():
    assert reverse("homepage:index") == "/"
    assert reverse("albums:list") == "/albums/"
    assert reverse("albums:detail", args=[3]) == "/albums/3/"
    assert reverse("artists:list") == "/artists/"
    assert reverse("artists:detail", args=[2]) == "/artists/2/"
    assert reverse("library:list") == "/collections/"
    assert reverse("library:detail", args=[1]) == "/collections/1/"


def test_navigation_uses_named_urls(client):
    text = client.get("/").content.decode("utf-8")
    for name in ("homepage:index", "albums:list", "artists:list",
                 "library:list"):
        assert f'href="{reverse(name)}"' in text


def test_length_filter_on_list_pages(client):
    albums, artists = load_data()[2], load_data()[1]
    text = client.get("/albums/").content.decode("utf-8")
    assert f"Всего альбомов: {len(albums)}" in text
    text = client.get("/artists/").content.decode("utf-8")
    assert f"Всего исполнителей: {len(artists)}" in text


def test_date_filter_formats_registration_date(client):
    user = load_data()[0][0]
    expected = user.registered_at.strftime("%d.%m.%Y")
    text = client.get("/collections/1/").content.decode("utf-8")
    assert expected in text


def test_default_filter_replaces_empty_title():
    user = User(1, "Алексей", date(2026, 9, 1))
    album = Album(1, "Title", Artist(1, "A", "RU", "Pop"), 2020, "Pop", user)
    album.title = ""
    html = render_to_string("albums/includes/album_card.html",
                            {"album": album})
    assert "Без названия" in html


@pytest.mark.parametrize("template, context, message", [
    ("albums/album_list.html", {"albums": []}, "Альбомы не найдены."),
    ("artists/artist_list.html", {"artists": []},
     "Исполнители не найдены."),
    ("library/collection_list.html", {"collections": []},
     "Коллекции не найдены."),
])
def test_empty_collections_are_handled_in_template(
    template, context, message
):
    assert message in render_to_string(template, context)


def test_html_is_escaped_in_templates():
    user = User(1, "Алексей", date(2026, 9, 1))
    artist = Artist(1, "<script>x</script>", "RU", "Pop")
    album = Album(1, "<b>Title</b>", artist, 2020, "Pop", user)
    html = render_to_string("albums/includes/album_card.html",
                            {"album": album})
    assert "&lt;b&gt;Title&lt;/b&gt;" in html
    assert "<script>x</script>" not in html


def test_album_status_include_has_two_states():
    user = User(1, "Алексей", date(2026, 9, 1))
    album = Album(1, "T", Artist(1, "A", "RU", "Pop"), 2020, "Pop", user)
    template = "albums/includes/album_status.html"
    assert "Не прослушан" in render_to_string(template, {"album": album})
    album.mark_listened()
    html = render_to_string(template, {"album": album})
    assert "Прослушан" in html
    assert "Не прослушан" not in html


@pytest.mark.parametrize("path", [
    "homepage/css/style.css",
    "homepage/js/main.js",
    "homepage/img/logo.png",
])
def test_static_files_are_found(path):
    assert finders.find(path)


def test_static_files_are_connected_in_base_template(client):
    text = client.get("/").content.decode("utf-8")
    assert "/static/homepage/css/style.css" in text
    assert "/static/homepage/js/main.js" in text
    assert "/static/homepage/img/logo.png" in text
    assert 'id="current-year"' in text


def test_header_shows_logo_and_brand_name_linked_to_home(client):
    text = client.get("/albums/").content.decode("utf-8")
    assert 'class="maestro-brand-name">Maestro</span>' in text
    home = reverse("homepage:index")
    assert f'<a href="{home}" class="maestro-brand">' in text
