import os
from dotenv import load_dotenv

load_dotenv()

# Конфиг для базы данных
DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME")
}

# Проверка обязательных переменных БД
for key, value in DB_CONFIG.items():
    if not value:
        raise ValueError(f"{key} not set in environment variables")

# Остальные ключи
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")
FREE_MESSAGE_LIMIT = 100

# Проверка остальных обязательных переменных
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN not set in .env")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not set in .env")
#if not YOOKASSA_SHOP_ID:
#    raise ValueError("YOOKASSA_SHOP_ID not set in .env")
#if not YOOKASSA_SECRET_KEY:
#    raise ValueError("YOOKASSA_SECRET_KEY not set in .env")
