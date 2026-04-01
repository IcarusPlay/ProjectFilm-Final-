# Модуль для записи поисковых запросов в MongoDB.
# Логика такая: если запрос уже был — просто увеличиваем счётчик,
# если новый — создаём документ. Так не плодим дубликаты в базе.

from pymongo import MongoClient
from datetime import datetime
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION


def get_mongo_client():
    """Создаёт и возвращает клиент MongoDB с таймаутом 2 секунды."""
    return MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)


def check_mongo_connection():
    """
    Проверяет доступность MongoDB через ping.
    Возвращает True если соединение успешно, False если нет.
    """
    client = get_mongo_client()
    try:
        client.admin.command('ping')
        return True
    except:
        return False
    finally:
        client.close()


def log_search_to_mongo(query_text, search_type, year=None, results_count=0):
    """
    Логирует поисковый запрос в MongoDB.

    Если такой запрос (текст + тип + год) уже есть в базе —
    увеличивает счётчик count на 1 и обновляет время last_searched.
    Если нет — создаёт новый документ (upsert).

    Пробелы в query_text обрезаются чтобы не плодить дубликаты типа
    "Drama" и " Drama " как разные записи.
    """
    # Убираем лишние пробелы по краям — монго чувствителен к этому
    query_text = query_text.strip()

    client = MongoClient(MONGO_URI)
    try:
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]

        # Уникальность документа определяется тройкой: текст + тип + год
        filter_query = {
            "query_text": query_text,
            "search_type": search_type,
            "year": year or "-"
        }

        update = {
            "$inc": {"count": 1},                       # увеличиваем счётчик
            "$set": {
                "results_count": results_count,          # сколько результатов вернул запрос
                "last_searched": datetime.now()          # когда последний раз искали
            }
            # timestamp намеренно убран — используем только last_searched
        }

        collection.update_one(filter_query, update, upsert=True)

    except Exception as e:
        print(f"Ошибка записи в Mongo: {e}")
    finally:
        client.close()
