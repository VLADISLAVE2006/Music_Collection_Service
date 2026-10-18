-- ==========================================
-- Maestro: SQL-запросы проекта
-- Проверка в SQLite CLI: sqlite3 data/maestro.sqlite < sql/queries.sql
-- Знак ? в запросах — параметр, значение передаётся отдельно из Python.
-- ==========================================


-- Запрос 1. Список исполнителей (выборка списка)
SELECT
    id,
    name,
    country,
    genre
FROM artists
ORDER BY name;


-- Запрос 2. Список альбомов (выборка списка)
SELECT
    id,
    title,
    release_year,
    genre
FROM albums
ORDER BY title;


-- Запрос 3. Список альбомов с исполнителем и звёздами оценки (JOIN)
-- Страница «Альбомы»
SELECT
    albums.id,
    albums.title,
    albums.release_year,
    albums.genre,
    artists.name AS artist_name,
    albums.rating,
    albums.is_listened
FROM albums
JOIN artists ON albums.artist_id = artists.id
ORDER BY albums.title;


-- Запрос 4. Карточка альбома по идентификатору (JOIN, WHERE, параметр)
-- Страница «Карточка альбома»
SELECT
    albums.id,
    albums.title,
    albums.release_year,
    albums.genre,
    albums.songs_count,
    albums.rating,
    albums.is_listened,
    artists.id AS artist_id,
    artists.name AS artist_name,
    users.name AS owner_name,
    CAST(strftime('%Y', 'now') AS INTEGER) - albums.release_year AS age
FROM albums
JOIN artists ON albums.artist_id = artists.id
JOIN users ON albums.user_id = users.id
WHERE albums.id = ?;


-- Запрос 5. Исполнители с количеством альбомов (LEFT JOIN, GROUP BY, COUNT)
-- Страница «Исполнители»
SELECT
    artists.id,
    artists.name,
    artists.country,
    artists.genre,
    COUNT(albums.id) AS albums_count
FROM artists
LEFT JOIN albums ON albums.artist_id = artists.id
GROUP BY artists.id, artists.name, artists.country, artists.genre
ORDER BY artists.name;


-- Запрос 6. Исполнитель по идентификатору (WHERE, параметр)
-- Страница «Карточка исполнителя»
SELECT
    id,
    name,
    country,
    genre
FROM artists
WHERE id = ?;


-- Запрос 7. Альбомы исполнителя (WHERE, параметр)
-- Страница «Карточка исполнителя»
SELECT
    id,
    title,
    release_year
FROM albums
WHERE artist_id = ?
ORDER BY release_year, title;


-- Запрос 8. Коллекции с владельцем и количеством альбомов (JOIN, GROUP BY)
-- Страница «Коллекции»
SELECT
    collections.id,
    users.name AS user_name,
    COUNT(collection_albums.album_id) AS albums_count
FROM collections
JOIN users ON collections.user_id = users.id
LEFT JOIN collection_albums
    ON collection_albums.collection_id = collections.id
GROUP BY collections.id, users.name
ORDER BY collections.id;


-- Запрос 9. Коллекция по идентификатору с владельцем (JOIN, WHERE, параметр)
-- Страница «Коллекция»
SELECT
    collections.id,
    users.name AS user_name,
    users.registered_at
FROM collections
JOIN users ON collections.user_id = users.id
WHERE collections.id = ?;


-- Запрос 10. Альбомы коллекции (JOIN трёх таблиц, WHERE, параметр)
-- Страница «Коллекция»
SELECT
    albums.id,
    albums.title,
    albums.rating,
    albums.is_listened,
    artists.name AS artist_name
FROM collection_albums
JOIN albums ON collection_albums.album_id = albums.id
JOIN artists ON albums.artist_id = artists.id
WHERE collection_albums.collection_id = ?
ORDER BY albums.title;


-- Запрос 11. Статистика коллекции (агрегатные функции COUNT, SUM, AVG)
-- Страница «Коллекция». AVG не учитывает альбомы без оценки (NULL)
SELECT
    COUNT(albums.id) AS total_albums,
    COALESCE(SUM(albums.songs_count), 0) AS total_songs,
    COUNT(DISTINCT albums.artist_id) AS total_artists,
    COALESCE(SUM(albums.is_listened), 0) AS listened_count,
    AVG(albums.rating) AS average_rating
FROM collection_albums
JOIN albums ON collection_albums.album_id = albums.id
WHERE collection_albums.collection_id = ?;


-- Запрос 12. Любимый жанр коллекции (GROUP BY, AVG, LIMIT)
-- Страница «Коллекция»: жанр с наивысшей средней оценкой
SELECT
    albums.genre,
    AVG(albums.rating) AS average_rating
FROM collection_albums
JOIN albums ON collection_albums.album_id = albums.id
WHERE collection_albums.collection_id = ?
  AND albums.rating IS NOT NULL
GROUP BY albums.genre
ORDER BY average_rating DESC, albums.genre
LIMIT 1;


-- Запрос 13. Поиск альбомов по жанру, минимальной оценке и названию
-- (WHERE с несколькими условиями, параметры). Страница «Поиск альбомов»
SELECT
    albums.id,
    albums.title,
    albums.release_year,
    albums.genre,
    artists.name AS artist_name,
    albums.rating,
    albums.is_listened
FROM albums
JOIN artists ON albums.artist_id = artists.id
WHERE (? = '' OR albums.genre = ?)
  AND COALESCE(albums.rating, 0) >= ?
  AND albums.title LIKE '%' || ? || '%'
ORDER BY albums.title;


-- Запрос 14. Список жанров без повторов (DISTINCT)
-- Страница «Поиск альбомов»: варианты выбора жанра
SELECT DISTINCT genre
FROM albums
ORDER BY genre;


-- Запрос 15. Статистика по жанрам (GROUP BY, COUNT, AVG, SUM)
-- Страница «Статистика»
SELECT
    albums.genre,
    COUNT(*) AS albums_count,
    AVG(albums.rating) AS average_rating,
    SUM(albums.songs_count) AS songs_count
FROM albums
GROUP BY albums.genre
ORDER BY albums_count DESC, albums.genre;


-- Запрос 16. Исполнители с количеством альбомов больше одного (HAVING)
-- Страница «Статистика»
SELECT
    artists.name AS artist_name,
    COUNT(albums.id) AS albums_count
FROM artists
JOIN albums ON albums.artist_id = artists.id
GROUP BY artists.id, artists.name
HAVING COUNT(albums.id) > 1
ORDER BY albums_count DESC, artists.name;


-- Запрос 17. Общие показатели (агрегатные функции)
-- Страница «Статистика». COUNT(rating) не считает NULL, COUNT(*) считает все
SELECT
    COUNT(*) AS albums_count,
    COUNT(albums.rating) AS rated_count,
    AVG(albums.rating) AS average_rating,
    COALESCE(SUM(albums.songs_count), 0) AS songs_count
FROM albums;


-- Запрос 18. Альбомы без оценки (проверка NULL)
SELECT
    id,
    title
FROM albums
WHERE rating IS NULL
ORDER BY title;


-- Запрос 19. Исполнители без альбомов (подзапрос NOT IN)
SELECT
    id,
    name
FROM artists
WHERE id NOT IN (SELECT artist_id FROM albums)
ORDER BY name;


-- Запрос 20. Три лучших альбома по оценке (ORDER BY, LIMIT, OFFSET)
SELECT
    title,
    rating
FROM albums
WHERE rating IS NOT NULL
ORDER BY rating DESC, title
LIMIT 3 OFFSET 0;


-- Запрос 21. Ещё не прослушанные альбомы (фильтрация по признаку)
SELECT
    id,
    title
FROM albums
WHERE is_listened = 0
ORDER BY title;
