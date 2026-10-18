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

from db import database  # noqa: E402
from db.database import get_connection  # noqa: E402
from db.import_json import DATA_DIR, import_all, load_json  # noqa: E402
from models import Album, Artist, User  # noqa: E402

PAGES = {
    "/": "homepage/index.html",
    "/albums/": "albums/album_list.html",
    "/albums/1/": "albums/album_detail.html",
    "/albums/search/": "albums/search.html",
    "/albums/statistics/": "albums/statistics.html",
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


@pytest.fixture(autouse=True)
def pages_database(tmp_path, monkeypatch):
    """Каждый тест работает с отдельной базой SQLite, созданной из JSON."""
    path = tmp_path / "pages.sqlite"
    monkeypatch.setattr(database, "DB_PATH", path)
    conn = get_connection(path)
    import_all(conn)
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def client():
    return Client(HTTP_HOST="127.0.0.1")


def template_names(response):
    return [template.name for template in response.templates]


def page_text(client, url):
    return client.get(url).content.decode("utf-8")


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


def test_data_comes_from_database_not_from_json(client, pages_database):
    assert "Обновлено в базе" not in page_text(client, "/albums/")
    conn = get_connection(pages_database)
    conn.execute(
        "UPDATE albums SET title = ? WHERE id = ?",
        ["Обновлено в базе", 1],
    )
    conn.commit()
    conn.close()
    assert "Обновлено в базе" in page_text(client, "/albums/")
    assert "Обновлено в базе" in page_text(client, "/albums/1/")


def test_context_is_passed_to_template(client):
    response = client.get("/albums/")
    albums = load_json(DATA_DIR / "albums.json")
    assert len(response.context["albums"]) == len(albums)
    row = response.context["albums"][0]
    assert row["artist_name"]
    detail = client.get("/albums/1/")
    assert detail.context["album"].id == 1
    assert detail.context["status"]


def test_album_page_shows_linked_objects(client):
    text = page_text(client, "/albums/1/")
    assert "After Hours" in text
    assert "The Weeknd" in text
    assert reverse("artists:detail", args=[1]) in text


def test_artist_page_lists_its_albums(client):
    text = page_text(client, "/artists/2/")
    assert "Daft Punk" in text
    assert "Discovery" in text
    assert "Random Access Memories" in text


def test_artists_list_shows_albums_count(client):
    text = page_text(client, "/artists/")
    assert "альбомов: 2" in text


def test_collection_page_shows_statistics_from_sql(client):
    response = client.get("/collections/1/")
    text = response.content.decode("utf-8")
    assert "Всего альбомов" in text
    assert "Средняя оценка" in text
    assert response.context["stats"]["total_albums"] == 5
    assert "Если вам нравится" in text


def test_search_form_without_parameters_shows_no_results(client):
    text = page_text(client, "/albums/search/")
    assert "Поиск альбомов" in text
    assert "Найдено альбомов" not in text


@pytest.mark.parametrize("query, expected, absent", [
    ("genre=Electronic", ["Discovery", "Random Access"], ["After Hours"]),
    ("min_rating=5", ["After Hours", "To Pimp"], ["Discovery"]),
    ("title=disc", ["Discovery"], ["After Hours"]),
    ("genre=Electronic&min_rating=4", ["Random Access"], ["Discovery"]),
])
def test_search_filters_albums(client, query, expected, absent):
    text = page_text(client, "/albums/search/?" + query)
    for item in expected:
        assert item in text
    for item in absent:
        assert item not in text


def test_search_without_results_shows_message(client):
    text = page_text(client, "/albums/search/?genre=Jazz")
    assert "По заданным условиям альбомов не найдено." in text


def test_search_is_safe_against_sql_injection(client):
    response = client.get(
        "/albums/search/", {"genre": "x' OR '1'='1", "title": "'; --"},
    )
    assert response.status_code == 200
    assert "По заданным условиям альбомов не найдено." in (
        response.content.decode("utf-8")
    )


def test_search_with_invalid_rating_does_not_fail(client):
    assert client.get("/albums/search/?min_rating=abc").status_code == 200
    assert client.get("/albums/search/?min_rating=99").status_code == 200


def test_statistics_page_shows_aggregates(client):
    response = client.get("/albums/statistics/")
    text = response.content.decode("utf-8")
    albums = load_json(DATA_DIR / "albums.json")
    assert f"Всего альбомов:</strong> {len(albums)}" in text
    assert "Альбомы по жанрам" in text
    assert "Daft Punk" in text
    assert response.context["totals"]["albums_count"] == len(albums)
    assert len(response.context["genres"]) == 4


def test_namespaced_urls():
    assert reverse("homepage:index") == "/"
    assert reverse("albums:list") == "/albums/"
    assert reverse("albums:detail", args=[3]) == "/albums/3/"
    assert reverse("albums:search") == "/albums/search/"
    assert reverse("albums:statistics") == "/albums/statistics/"
    assert reverse("artists:list") == "/artists/"
    assert reverse("artists:detail", args=[2]) == "/artists/2/"
    assert reverse("library:list") == "/collections/"
    assert reverse("library:detail", args=[1]) == "/collections/1/"


def test_navigation_uses_named_urls(client):
    text = page_text(client, "/")
    for name in ("homepage:index", "albums:list", "artists:list",
                 "library:list", "albums:statistics"):
        assert f'href="{reverse(name)}"' in text


def test_length_filter_on_list_pages(client):
    albums = load_json(DATA_DIR / "albums.json")
    artists = load_json(DATA_DIR / "artists.json")
    assert f"Всего альбомов: {len(albums)}" in page_text(client, "/albums/")
    assert (
        f"Всего исполнителей: {len(artists)}"
        in page_text(client, "/artists/")
    )


def test_date_filter_formats_registration_date(client):
    user = load_json(DATA_DIR / "users.json")[0]
    expected = date.fromisoformat(user["registered_at"]).strftime("%d.%m.%Y")
    assert expected in page_text(client, "/collections/1/")


def album_row(**changes):
    row = {
        "id": 1, "title": "Title", "artist_name": "Artist",
        "release_year": 2020, "genre": "Pop", "rating": None,
        "is_listened": 0,
    }
    row.update(changes)
    return row


def test_default_filter_replaces_empty_title():
    html = render_to_string("albums/includes/album_card.html",
                            {"album": album_row(title="")})
    assert "Без названия" in html


def test_stars_filter_in_album_card():
    empty = render_to_string("albums/includes/album_card.html",
                             {"album": album_row()})
    rated = render_to_string("albums/includes/album_card.html",
                             {"album": album_row(rating=4)})
    assert "☆☆☆☆☆" in empty
    assert "★★★★☆" in rated


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
    row = album_row(title="<b>Title</b>", artist_name="<script>x</script>")
    html = render_to_string("albums/includes/album_card.html",
                            {"album": row})
    assert "&lt;b&gt;Title&lt;/b&gt;" in html
    assert "&lt;script&gt;" in html
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
    text = page_text(client, "/")
    assert "/static/homepage/css/style.css" in text
    assert "/static/homepage/js/main.js" in text
    assert "/static/homepage/img/logo.png" in text
    assert 'id="current-year"' in text


def test_header_shows_logo_and_brand_name_linked_to_home(client):
    text = page_text(client, "/albums/")
    assert 'class="maestro-brand-name">Maestro</span>' in text
    home = reverse("homepage:index")
    assert f'<a href="{home}" class="maestro-brand">' in text
