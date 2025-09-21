#!/usr/bin/env python3
"""
Скрипт для исправления премиум подписки пользователя 627875032
Устанавливает правильные данные в БД
Использует универсальный DatabaseUtils для устранения дублирования кода.
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к shared модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.database_utils import fix_premium_subscription

if __name__ == "__main__":
    asyncio.run(fix_premium_subscription())
