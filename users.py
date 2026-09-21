"""Функции работы с пользователями.

Пользователь — словарь: {"id", "name", "registered_at"}, где дата
регистрации хранится строкой в формате ГГГГ-ММ-ДД.
"""
from datetime import date
from typing import Dict, List, Optional

from utils import next_id


def add_user(users: List[Dict], name: str) -> Dict:
    """Добавить пользователя в список и вернуть созданную запись.

    Raises:
        ValueError: если имя пользователя пустое.
    """
    if not name.strip():
        raise ValueError("Имя пользователя не может быть пустым")
    user = {
        "id": next_id(users),
        "name": name.strip(),
        "registered_at": date.today().isoformat(),
    }
    users.append(user)
    return user


def find_user(users: List[Dict], query: str) -> List[Dict]:
    """Найти пользователей по подстроке имени (без учёта регистра)."""
    query = query.strip().lower()
    return [user for user in users if query in user["name"].lower()]


def find_user_by_id(users: List[Dict], user_id: int) -> Optional[Dict]:
    """Найти пользователя по идентификатору."""
    for user in users:
        if user["id"] == user_id:
            return user
    return None


def find_user_by_name(users: List[Dict], name: str) -> Optional[Dict]:
    """Найти пользователя по точному имени (без учёта регистра)."""
    name = name.strip().lower()
    for user in users:
        if user["name"].lower() == name:
            return user
    return None


def show_users(users: List[Dict]) -> None:
    """Вывести список пользователей."""
    if not users:
        print("Список пользователей пуст.")
        return
    for user in users:
        print(
            f"[{user['id']}] {user['name']} "
            f"(зарегистрирован {user['registered_at']})"
        )
