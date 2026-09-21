# Music Collection Service — сервис музыкальных коллекций

Консольное приложение для управления личной музыкальной коллекцией:
альбомы, исполнители, оценки, статус прослушивания и рекомендации.

## Возможности

- вход в систему по имени (новый пользователь регистрируется);
- просмотр коллекции и подробная карточка альбома;
- добавление альбомов и удаление из коллекции;
- оценка альбома (1–5) и отметка «прослушан»;
- поиск по названию альбома или исполнителю;
- фильтрация по жанру и сортировка (оценка, год, название);
- статистика коллекции (песни, альбомы, исполнители, средняя оценка);
- рекомендации на основе оценок;
- сохранение данных между запусками в JSON-файлах.

## Предметная область

Основные сущности: пользователь, исполнитель, альбом, коллекция.
Данные представлены словарями, коллекции — списками словарей;
поведение реализовано функциями.

Бизнес-правила:

- оценка альбома от 1 до 5;
- год выпуска не может быть в будущем;
- название альбома и имя исполнителя не могут быть пустыми;
- один альбом нельзя добавить в коллекцию дважды.

## Формат данных

Данные хранятся в каталоге `data/` в JSON-файлах:

- `users.json` — `id`, `name`, `registered_at`;
- `artists.json` — `id`, `name`, `country`, `genre`;
- `albums.json` — `id`, `title`, `artist_id`, `release_year`, `genre`,
  `songs_count`, `rating`, `is_listened`, `user_id`;
- `collections.json` — `id`, `user_id`, `album_ids`.

При запуске данные читаются из файлов, при завершении — сохраняются.
Некорректный JSON и отсутствующие файлы не приводят к аварийному
завершению программы.

## Структура проекта

```text
music_collection/
├── README.md
├── requirements.txt
├── pytest.ini
├── .flake8
├── .gitignore
├── main.py
├── artists.py
├── users.py
├── albums.py
├── collection.py
├── storage.py
├── utils.py
├── data/
│   ├── users.json
│   ├── artists.json
│   ├── albums.json
│   └── collections.json
└── tests/
    ├── test_artists.py
    ├── test_users.py
    ├── test_albums.py
    ├── test_collection.py
    └── test_storage.py
```

## Модули и функции

| Модуль | Назначение и функции |
| --- | --- |
| `main.py` | меню и пользовательские сценарии, `main()` |
| `artists.py` | `add_artist`, `find_artist`, `find_artist_by_id`, `find_artist_by_name`, `get_artist_name`, `show_artists` |
| `users.py` | `add_user`, `find_user`, `find_user_by_id`, `find_user_by_name`, `show_users` |
| `albums.py` | `create_album`, `validate_rating`, `validate_year`, `rate_album`, `mark_album_listened`, `find_album`, `find_album_by_id`, `filter_albums_by_genre`, `sort_albums`, `get_album_status`, `get_recommendation`, `get_rating_stars`, `format_album`, `show_albums` |
| `collection.py` | `create_collection`, `get_user_collection`, `get_collection_albums`, `is_album_in_collection`, `add_album_to_collection`, `remove_album_from_collection`, `get_statistics`, `get_favorite_genre`, `get_collection_recommendation`, `show_statistics` |
| `storage.py` | `load_*` / `save_*` для пользователей, исполнителей, альбомов и коллекций |
| `utils.py` | `input_int`, `input_text`, `next_id` |

Функции `get_album_status()`, `get_rating_stars()` и
`get_recommendation()` перенесены из начального сценария ПР1.
Для сортировки используется lambda-функция, для фильтрации — генератор.

## Запуск программы

```text
pip install -r requirements.txt
python main.py
```

## Тестирование

```text
pytest -v
```

## Проверка качества кода

```text
flake8 .
```
