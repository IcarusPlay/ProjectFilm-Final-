# Модуль для чтения статистики из MongoDB.
# Здесь два запроса: топ популярных и последние 5 поисков.
# Оба используют одну коллекцию, просто сортируют по разным полям.

from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION


def get_popular_searches_mongo(limit=5):
    """
    Возвращает топ-N самых популярных запросов из MongoDB,
    отсортированных по полю count (количество обращений) по убыванию.

    Каждый элемент списка содержит:
    - query_text: текст запроса
    - search_type: тип (keyword / genre)
    - year: год или диапазон лет (для жанрового поиска)
    - count: сколько раз этот запрос делали
    """
    client = MongoClient(MONGO_URI)
    try:
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]

        results = list(
            collection.find(
                {},
                {"query_text": 1, "search_type": 1, "year": 1, "count": 1, "_id": 0}
            )
            .sort("count", -1)
            .limit(limit)
        )

        # Собираем чистый список — без лишних полей MongoDB
        return [
            {
                "query_text": doc.get("query_text", ""),
                "search_type": doc.get("search_type", ""),
                "year": doc.get("year", "-"),
                "count": doc.get("count", 1)
            }
            for doc in results
        ]

    except Exception as e:
        print(f"Ошибка чтения из Mongo: {e}")
        return []
    finally:
        client.close()


def get_last_searches_mongo(limit=5):
    """
    Возвращает последние N поисковых запросов из MongoDB,
    отсортированных по полю last_searched (время последнего поиска) по убыванию.

    Используется для пункта меню "Последние запросы".
    """
    client = MongoClient(MONGO_URI)
    try:
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]

        results = list(
            collection.find(
                {},
                {"query_text": 1, "search_type": 1, "year": 1, "last_searched": 1, "_id": 0}
            )
            .sort("last_searched", -1)
            .limit(limit)
        )
        return results

    except Exception as e:
        print(f"Ошибка чтения из Mongo: {e}")
        return []
    finally:
        client.close()
