import os

import django
import pytest
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "maestro.settings")
django.setup()


@pytest.fixture
def client():
    return Client(HTTP_HOST="localhost")


@pytest.mark.parametrize("url", [
    "/",
    "/albums/",
    "/albums/1/",
    "/artists/",
    "/artists/1/",
    "/collections/",
    "/collections/1/",
])
def test_pages_return_200(client, url):
    response = client.get(url)
    assert response.status_code == 200
    assert "bootstrap" in response.content.decode("utf-8")


@pytest.mark.parametrize("url", [
    "/albums/999/",
    "/artists/999/",
    "/collections/999/",
])
def test_missing_object_returns_404(client, url):
    assert client.get(url).status_code == 404


def test_unknown_url_returns_404(client):
    assert client.get("/nothing/").status_code == 404


def test_album_page_shows_linked_objects(client):
    text = client.get("/albums/1/").content.decode("utf-8")
    assert "After Hours" in text
    assert "The Weeknd" in text
    assert "/artists/1/" in text


def test_collection_page_shows_statistics(client):
    text = client.get("/collections/1/").content.decode("utf-8")
    assert "Всего альбомов" in text
    assert "Средняя оценка" in text
