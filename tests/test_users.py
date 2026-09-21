from datetime import date

import pytest

from users import add_user, find_user, find_user_by_id, find_user_by_name


def test_add_user():
    users = []
    user = add_user(users, "Владислав")
    assert users == [user]
    assert user["id"] == 1
    assert user["registered_at"] == date.today().isoformat()


def test_add_user_empty_name_forbidden():
    with pytest.raises(ValueError):
        add_user([], "")


def test_find_user():
    users = []
    user = add_user(users, "Владислав")
    assert find_user(users, "влад") == [user]
    assert find_user(users, "мария") == []


def test_find_user_by_id_and_name():
    users = []
    user = add_user(users, "Владислав")
    assert find_user_by_id(users, 1) is user
    assert find_user_by_id(users, 5) is None
    assert find_user_by_name(users, "ВЛАДИСЛАВ") is user
    assert find_user_by_name(users, "Иван") is None
