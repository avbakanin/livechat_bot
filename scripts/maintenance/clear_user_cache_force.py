#!/usr/bin/env python3
"""
Скрипт для принудительной очистки кэша пользователя через код
Использует универсальный DatabaseUtils для устранения дублирования кода.
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к shared модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.database_utils import clear_user_cache_force

if __name__ == "__main__":
    asyncio.run(clear_user_cache_force())
