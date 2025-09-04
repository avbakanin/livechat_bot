import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "user": os.getenv("DB_USER") or raise ValueError("DB_USER not set in .env"),
    "password": os.getenv("DB_PASSWORD") or raise ValueError("DB_PASSWORD not set in .env"),
    "database": os.getenv("DB_NAME") or raise ValueError("DB_NAME not set in .env"),
    "host": os.getenv("DB_HOST") or raise ValueError("DB_HOST not set in .env"),
    "port": int(os.getenv("DB_PORT") or raise ValueError("DB_PORT not set in .env"))
}

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or raise ValueError("TELEGRAM_TOKEN not set in .env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or raise ValueError("OPENAI_API_KEY not set in .env")
YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID") or raise ValueError("YOOKASSA_SHOP_ID not set in .env")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY") or raise ValueError("YOOKASSA_SECRET_KEY not set in .env")
FREE_MESSAGE_LIMIT = 100