# Модуль для вывода результатов поиска в консоль.
# Вынесен отдельно чтобы не мусорить в main.py логикой форматирования.


def print_movies(movies, lang):
    """
    Выводит список фильмов в консоль в читаемом виде.
    Если список пустой — показывает сообщение об ошибке из локализации.
    Каждый фильм выводится в формате: -> Название (Год)
    """
    if not movies:
        print(f"\n{lang['invalid_input']}")
        return

    print(f"\nНайдено: {len(movies)}")
    for m in movies:
        # Пробуем разные ключи — на случай если структура словаря отличается
        title = m.get('title') or m.get('name') or "Без названия"
        year = m.get('year') or m.get('release_year') or "????"
        print(f" -> {title} ({year})")
