import pytest

from collection import (
    add_album_to_collection,
    create_collection,
    get_collection_albums,
    get_collection_recommendation,
    get_favorite_genre,
    get_statistics,
    get_user_collection,
    is_album_in_collection,
    remove_album_from_collection,
)


@pytest.fixture
def collection():
    return create_collection([], 1)


def test_create_and_get_user_collection():
    collections = []
    created = create_collection(collections, 1)
    assert created["album_ids"] == []
    assert get_user_collection(collections, 1) is created
    assert get_user_collection(collections, 2) is None


def test_add_album_to_collection(collection):
    albums = []
    album = add_album_to_collection(
        collection, albums, "After Hours", 1, 2020, "Pop", 14
    )
    assert album is not None
    assert album["user_id"] == 1
    assert albums == [album]
    assert collection["album_ids"] == [album["id"]]
    assert get_collection_albums(collection, albums) == [album]


def test_duplicate_album_forbidden(collection):
    albums = []
    add_album_to_collection(collection, albums, "After Hours", 1, 2020, "Pop")
    second = add_album_to_collection(
        collection, albums, "after hours", 1, 2020, "Pop"
    )
    assert second is None
    assert len(albums) == 1
    assert len(collection["album_ids"]) == 1


def test_same_title_other_artist_allowed(collection):
    albums = []
    add_album_to_collection(collection, albums, "Greatest", 1, 2020, "Pop")
    other = add_album_to_collection(
        collection, albums, "Greatest", 2, 2019, "Rock"
    )
    assert other is not None


def test_invalid_album_data_raises(collection):
    with pytest.raises(ValueError):
        add_album_to_collection(collection, [], "", 1, 2020, "Pop")


def test_is_album_in_collection(collection):
    albums = []
    add_album_to_collection(collection, albums, "After Hours", 1, 2020, "Pop")
    mine = get_collection_albums(collection, albums)
    assert is_album_in_collection(mine, "AFTER HOURS", 1)
    assert not is_album_in_collection(mine, "After Hours", 2)


def test_remove_album(collection):
    albums = []
    album = add_album_to_collection(
        collection, albums, "After Hours", 1, 2020, "Pop"
    )
    assert remove_album_from_collection(collection, albums, album["id"])
    assert albums == []
    assert collection["album_ids"] == []
    assert not remove_album_from_collection(collection, albums, album["id"])


def test_removed_album_can_be_added_again(collection):
    albums = []
    first = add_album_to_collection(
        collection, albums, "After Hours", 1, 2020, "Pop"
    )
    remove_album_from_collection(collection, albums, first["id"])
    again = add_album_to_collection(
        collection, albums, "After Hours", 1, 2020, "Pop"
    )
    assert again is not None


def test_statistics_and_recommendation(collection):
    albums = []
    first = add_album_to_collection(
        collection, albums, "After Hours", 1, 2020, "Pop", 14
    )
    second = add_album_to_collection(
        collection, albums, "Discovery", 2, 2001, "Electronic", 14
    )
    first.update(rating=5, is_listened=True)
    second.update(rating=3, is_listened=True)
    mine = get_collection_albums(collection, albums)
    stats = get_statistics(mine)
    assert stats["total_albums"] == 2
    assert stats["total_songs"] == 28
    assert stats["total_artists"] == 2
    assert stats["listened_count"] == 2
    assert stats["average_rating"] == 4
    assert get_favorite_genre(mine) == "Pop"
    assert "Pop" in get_collection_recommendation(mine)


def test_statistics_of_empty_collection():
    stats = get_statistics([])
    assert stats["total_albums"] == 0
    assert stats["average_rating"] is None
    assert get_favorite_genre([]) is None
    assert "Оцените" in get_collection_recommendation([])
