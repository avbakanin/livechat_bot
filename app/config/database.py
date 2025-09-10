"""
Database configuration settings.
"""
import os
from typing import TypedDict, Optional
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig(TypedDict):
    """Database configuration type."""
    user: Optional[str]
    password: Optional[str]
    host: Optional[str]
    port: int
    database: Optional[str]


DATABASE_CONFIG: DatabaseConfig = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME")
}
