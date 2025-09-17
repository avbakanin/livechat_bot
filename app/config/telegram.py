"""
Telegram bot configuration settings.
"""
import os
from typing import Optional, TypedDict

from dotenv import load_dotenv

load_dotenv()


class TelegramConfig(TypedDict):
    """Telegram bot configuration type."""

    token: Optional[str]
    allowed_user_ids: set[int]


TELEGRAM_CONFIG: TelegramConfig = {
    "token": os.getenv("TELEGRAM_TOKEN"),
    "allowed_user_ids": {627875032, 1512454100, 826795306},  # Allowed user IDs
}
