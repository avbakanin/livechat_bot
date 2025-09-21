#!/usr/bin/env python3
"""
Скрипт для проверки переводов reset_info с эмодзи часов во всех языках
Использует универсальный TranslationChecker для устранения дублирования кода.
"""

import sys
from pathlib import Path

# Добавляем путь к shared модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.translation_checker import check_reset_info_with_emoji

if __name__ == "__main__":
    check_reset_info_with_emoji()
