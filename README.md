# Music Collection Service — сервис музыкальных коллекций

Консольное приложение для управления личной музыкальной коллекцией:
альбомы, исполнители, оценки, статус прослушивания и рекомендации.

## Назначение

Приложение позволяет вести личную музыкальную коллекцию: хранить альбомы
и исполнителей, оценивать прослушанное и получать рекомендации.

## Целевая аудитория

Слушатели музыки, которым нужен простой способ учитывать свои альбомы,
оценки и статус прослушивания.

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
Каждая сущность — класс (`User`, `Artist`, `Album`, `Collection`)
в пакете `models/`; рядом с классом лежат функции поиска и управления
списками объектов. Связи между объектами хранятся ссылками на объекты,
а в JSON записываются идентификаторами.

Бизнес-правила:

- оценка альбома от 1 до 5;
- год выпуска не может быть в будущем;
- название альбома и имя исполнителя не могут быть пустыми;
- один альбом нельзя добавить в коллекцию дважды.

## Основные сущности и классы

### User — пользователь

- атрибуты: `id`, `name`, `registered_at`;
- методы: `from_data()` (classmethod, создание из записи JSON),
  `__str__()`.

### Artist — исполнитель

- атрибуты: `id`, `name`, `country`, `genre`;
- методы: `from_data()` (classmethod), `__str__()`.

### Album — альбом

- атрибуты: `id`, `title`, `artist` (объект `Artist`), `release_year`,
  `genre`, `user` (объект `User`), `songs_count`, `rating`,
  `is_listened`;
- методы: `rate()` (оценка 1–5, альбом считается прослушанным),
  `mark_listened()`, `age()`, `__str__()`;
- статические методы: `validate_rating()`, `validate_year()`.

### Collection — коллекция пользователя

- атрибуты: `id`, `user` (объект `User`), `albums` (список объектов
  `Album`);
- методы: `contains()`, `add_album()`, `remove_album()`, `favorite_genre()`,
  `__str__()`;
- свойства: `total_albums`, `total_songs`, `total_artists`,
  `listened_count`, `average_rating`.

## Взаимодействие объектов

```text
User ──владеет──> Collection ──содержит──> Album ──исполняет──> Artist
  └───────────────────── Album.user ──────────┘
```

- `Album` хранит ссылки на объекты `Artist` и `User`, а не их
  идентификаторы (`album.artist.name`, `album.user.id`);
- `Collection` хранит список объектов `Album` и проверяет, что альбом
  принадлежит владельцу коллекции и не дублируется;
- `add_album_to_collection()` создаёт `Album`, добавляет его в коллекцию
  и в общий список альбомов; `remove_album_from_collection()` удаляет
  из обоих;
- при загрузке `storage.py` по `artist_id`, `user_id` и `album_ids`
  находит объекты и восстанавливает ссылки, при сохранении преобразует
  ссылки обратно в идентификаторы;
- альбом без найденного исполнителя или пользователя не создаётся.

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
MyProject/
├── README.md
├── requirements.txt
├── pytest.ini
├── .flake8
├── .gitignore
├── main.py
├── storage.py
├── utils.py
├── models/
│   ├── __init__.py
│   ├── users.py
│   ├── artists.py
│   ├── albums.py
│   └── collection.py
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
| `models/users.py` | класс `User` (`from_data`); `add_user`, `find_user`, `find_user_by_id`, `find_user_by_name`, `show_users` |
| `models/artists.py` | класс `Artist` (`from_data`); `add_artist`, `find_artist`, `find_artist_by_id`, `find_artist_by_name`, `show_artists` |
| `models/albums.py` | класс `Album` (`validate_rating`, `validate_year`, `rate`, `mark_listened`, `age`); `get_rating_stars`, `get_album_status`, `get_recommendation`, `find_album`, `find_album_by_id`, `filter_albums_by_genre`, `sort_albums`, `show_albums` |
| `models/collection.py` | класс `Collection` (`contains`, `add_album`, `remove_album`, `total_albums`, `total_songs`, `total_artists`, `listened_count`, `average_rating`, `favorite_genre`); `create_collection`, `get_user_collection`, `add_album_to_collection`, `remove_album_from_collection`, `get_collection_recommendation`, `show_statistics` |
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

## План развития

На следующих этапах планируется:

- разработка веб-приложения на Django;
- подключение базы данных;
- реализация пользователей и авторизации;
- разработка API;
- контейнеризация приложения;
- настройка CI/CD.
