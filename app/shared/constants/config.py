import os
from typing import Optional, TypedDict

from dotenv import load_dotenv

load_dotenv()


class DBConfig(TypedDict):
    user: Optional[str]
    password: Optional[str]
    host: Optional[str]
    port: int
    database: Optional[str]


class AppConfig(TypedDict):
    TELEGRAM_TOKEN: Optional[str]
    OPENAI_API_KEY: Optional[str]
    YOOKASSA_SHOP_ID: Optional[str]
    YOOKASSA_SECRET_KEY: Optional[str]
    FREE_MESSAGE_LIMIT: int


DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME"),
}

APP_CONFIG: AppConfig = {
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "YOOKASSA_SHOP_ID": os.getenv("YOOKASSA_SHOP_ID"),
    "YOOKASSA_SECRET_KEY": os.getenv("YOOKASSA_SECRET_KEY"),
    "FREE_MESSAGE_LIMIT": 100,
}

# ОТКЛЮЧИТЬ
# Проверка обязательных переменных окружения
# for key, value in DB_CONFIG.items():
#     if not value:
#         raise ValueError(f"{key} not set in DB_CONFIG .env variables")
# for key, value in APP_CONFIG.items():
#     if not value:
#         raise ValueError(f"{key} not set in APP_CONFIG .env variables")
