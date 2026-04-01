# Конфигурация проекта — все настройки подключений берутся из .env файла.
# Это стандартная практика: секреты (пароли, URI) не хранятся в коде,
# а лежат в .env который добавлен в .gitignore и не попадает в репозиторий.

from dotenv import load_dotenv
import os

# Загружаем переменные из .env в окружение
load_dotenv()

# --- MySQL ---
# Настройки подключения к основной базе данных (Sakila)
MYSQL_CONFIG = {
    "host":     os.getenv("MYSQL_READ_HOST"),
    "port":     int(os.getenv("MYSQL_READ_PORT", 3306)),
    "user":     os.getenv("MYSQL_READ_USER"),
    "password": os.getenv("MYSQL_READ_PASSWORD"),
    "database": os.getenv("MYSQL_READ_DB"),
}

# --- MongoDB ---
# URI, имя базы и коллекции — тоже из .env, чтобы легко менять без правки кода
MONGO_URI        = os.getenv("MONGO_URI")
MONGO_DB         = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

# Список жанров из базы данных Sakila.
# Используется в меню поиска по жанру — показываем пользователю что вводить.
GENRES = [
    "Action", "Animation", "Children", "Classics", "Comedy",
    "Documentary", "Drama", "Family", "Foreign", "Games",
    "Horror", "Music", "New", "Sci-Fi", "Sports",
    "Travel"
]
