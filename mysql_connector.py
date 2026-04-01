# Модуль для работы с MySQL (база данных Sakila).
# Здесь все запросы к фильмам — по ключевому слову и по жанру+году.
# Соединение открывается и закрывается при каждом запросе — так надёжнее.

import pymysql
from config import MYSQL_CONFIG


def get_connection():
    """Создаёт и возвращает соединение с MySQL используя настройки из config.py."""
    return pymysql.connect(
        **MYSQL_CONFIG,
        cursorclass=pymysql.cursors.DictCursor  # результаты сразу как словари
    )


def check_mysql_connection():
    """
    Проверяет доступность MySQL.
    Возвращает True если соединение успешно, False если нет.
    """
    try:
        conn = get_connection()
        conn.close()
        return True
    except:
        return False


def search_keyword(keyword, offset=0):
    """
    Ищет фильмы по ключевому слову в названии (LIKE %keyword%).
    Возвращает до 10 результатов, поддерживает offset для пагинации.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = f"SELECT title, release_year FROM film WHERE title LIKE %s LIMIT 10 OFFSET {int(offset)}"
            cursor.execute(sql, ("%" + keyword + "%",))
            return cursor.fetchall()
    finally:
        conn.close()


def search_genre_year(genre, y1, y2, offset=0):
    """
    Ищет фильмы по жанру и диапазону годов.
    Делает JOIN трёх таблиц: film → film_category → category.
    Возвращает до 10 результатов, поддерживает offset для пагинации.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = f"""
            SELECT f.title, f.release_year
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            WHERE c.name = %s AND f.release_year BETWEEN %s AND %s
            LIMIT 10 OFFSET {int(offset)}
            """
            cursor.execute(sql, (genre, int(y1), int(y2)))
            return cursor.fetchall()
    finally:
        conn.close()
