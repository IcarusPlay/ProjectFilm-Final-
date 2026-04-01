# Главный модуль проекта — точка входа и основное меню.
# Здесь собирается всё вместе: выбор языка, меню, обработка ввода пользователя.
# Вся бизнес-логика вынесена в отдельные модули (mysql_connector, log_writer и т.д.)

import json
import os
from config import GENRES

from mysql_connector import check_mysql_connection, search_keyword, search_genre_year
from log_writer import check_mongo_connection, log_search_to_mongo
from log_stats import get_popular_searches_mongo, get_last_searches_mongo
from formatter import print_movies


def choose_language():
    """
    Показывает меню выбора языка и загружает нужный JSON-файл локализации.
    Если файл не найден — возвращает базовый словарь на английском как запасной вариант.
    """
    print("\n" + "="*40)
    print("        LANGUAGE SELECTION")
    print("="*40)
    print("1 Русский")
    print("2 Українська")
    print("3 English")
    print("4 Deutsch")
    print("="*40)

    choice = input("Select language: ")
    languages = {"1": "ru.json", "2": "ua.json", "3": "en.json", "4": "de.json"}
    lang_file = languages.get(choice, "en.json")  # по умолчанию английский
    path = os.path.join("lang", lang_file)

    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Language file not found, using default English.")
        return {
            "menu_title": "Menu", "menu_1": "Search by keyword", "menu_2": "Search by genre",
            "menu_3": "Popular", "menu_language": "Language", "menu_4": "Exit", "choose": "Choice: ",
            "enter_keyword": "Keyword: ", "enter_genre": "Genre: ", "year_from": "From: ",
            "year_to": "To: ", "bye": "Bye!", "invalid_input": "Nothing found."
        }


def show_menu(lang):
    """Выводит главное меню с пунктами на выбранном языке."""
    print("\n" + "="*40)
    print(f"        {lang['menu_title']}")
    print("="*40)
    print(f"1  {lang['menu_1']}")
    print(f"2  {lang['menu_2']}")
    print(f"3  {lang['menu_3']}")
    print(f"4  {lang.get('menu_history', 'Last searches')}")
    print(f"5  {lang['menu_language']}")
    print(f"6  {lang['menu_4']}")
    print("7  Database status")
    print("="*40)


def show_db_status():
    """Проверяет и выводит статус подключения к MySQL и MongoDB."""
    print("\n" + "="*40)
    print("        DATABASE STATUS")
    print("="*40)
    print("MySQL:", "OK" if check_mysql_connection() else "ERROR")
    print("MongoDB:", "OK" if check_mongo_connection() else "ERROR")
    print("="*40)


def menu(lang):
    """
    Основной цикл программы. Принимает ввод пользователя и вызывает нужную функцию.

    Пункты меню:
    1 — поиск по ключевому слову (логируется без года)
    2 — поиск по жанру и диапазону годов (показывает список жанров перед вводом)
    3 — топ популярных запросов из MongoDB
    4 — последние 5 запросов из MongoDB
    5 — смена языка
    6 — выход
    7 — статус баз данных
    """
    while True:
        show_menu(lang)
        choice = input(lang["choose"]).strip()

        # Пустой ввод — просто просим выбрать снова
        if not choice:
            print(f"\n{lang.get('search_menu_title', 'Выберите вид поиска:')}")
            continue

        if choice == "1":
            keyword = input(lang["enter_keyword"]).strip()
            if not keyword:
                print(f"\n{lang.get('no_movie_found', 'Такого фильма нет.')}")
                continue

            movies = search_keyword(keyword)
            count = len(movies)

            if count > 0:
                # Год для keyword-поиска не логируем — он не имеет смысла
                log_search_to_mongo(
                    query_text=keyword,
                    search_type="keyword",
                    results_count=count
                )
                print_movies(movies, lang)
            else:
                print(f"\n{lang.get('no_movie_found', 'Такого фильма нет.')}")

        elif choice == "2":
            # Показываем доступные жанры чтобы пользователь не гадал что вводить
            print(f"\n{lang.get('available_genres', 'Available genres:')} {', '.join(GENRES)}")
            genre = input(lang["enter_genre"]).strip()
            y1 = input(lang["year_from"]).strip()
            y2 = input(lang["year_to"]).strip()

            # Проверяем что жанр не пустой и годы — числа
            if not genre or (y1 and not y1.isdigit()) or (y2 and not y2.isdigit()):
                print(f"\n{lang.get('invalid_genre_year', 'Неверный ввод года или жанра')}")
                continue

            movies = search_genre_year(genre, y1, y2)
            count = len(movies)
            year_range = f"{y1}-{y2}"

            if count > 0:
                log_search_to_mongo(genre, "genre", year=year_range, results_count=count)
                print_movies(movies, lang)
            else:
                print(f"\n{lang.get('no_movie_found', 'Такого фильма нет.')}")

        elif choice == "3":
            # Популярные запросы — топ-5 по количеству обращений
            popular = get_popular_searches_mongo()
            print("\n" + "=" * 40)
            print(f"        {lang.get('popular_title', 'POPULAR SEARCHES')}")
            print("=" * 40)

            if not popular:
                print(lang.get('history_empty', 'No searches yet.'))
            else:
                # Считаем итого по типам для статистики внизу
                keyword_total = sum(i.get('count', 1) for i in popular if i.get('search_type') == 'keyword')
                genre_total   = sum(i.get('count', 1) for i in popular if i.get('search_type') == 'genre')

                for i, item in enumerate(popular, 1):
                    s_type      = item.get('search_type', '')
                    text        = item.get('query_text', '')
                    year        = item.get('year', '-')
                    count       = item.get('count', 1)
                    label       = lang.get('label_genres', 'Genre') if s_type == 'genre' else lang.get('label_keyword', 'Keyword')
                    year_label  = lang.get('label_year', 'Year')
                    times_label = lang.get('label_times', 'times')

                    print(f"{i}. {label}: {text} | {year_label}: {year} | {count} {times_label}")

                print("-" * 40)
                print(f"{lang.get('label_keyword', 'Keyword')} {lang.get('label_total', 'total')}: {keyword_total}")
                print(f"{lang.get('label_genres', 'Genre')} {lang.get('label_total', 'total')}: {genre_total}")
            print("=" * 40)

        elif choice == "4":
            # Последние 5 запросов — сортировка по last_searched
            last = get_last_searches_mongo(5)
            print("\n" + "=" * 40)
            print(f"        {lang.get('history_title', 'LAST 5 SEARCHES')}")
            print("=" * 40)

            if not last:
                print(lang.get('history_empty', 'No searches yet.'))
            else:
                for i, item in enumerate(last, 1):
                    s_type  = item.get('search_type', '')
                    text    = item.get('query_text', '')
                    year    = item.get('year', '')
                    ts      = item.get('last_searched', '')
                    label   = lang.get('label_genres', 'Genre') if s_type == 'genre' else lang.get('label_keyword', 'Keyword')
                    ts_str  = ts.strftime("%d.%m.%Y %H:%M") if hasattr(ts, 'strftime') else str(ts)
                    print(f"{i}. [{ts_str}] {label}: {text} | {lang.get('label_year', 'Year')}: {year}")
            print("=" * 40)

        elif choice == "5":
            # Меняем язык — перезагружаем словарь локализации
            lang = choose_language()

        elif choice == "6":
            print(lang["bye"])
            break

        elif choice == "7":
            show_db_status()


if __name__ == "__main__":
    language = choose_language()
    menu(language)
