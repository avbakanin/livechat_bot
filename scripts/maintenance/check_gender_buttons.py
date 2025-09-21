#!/usr/bin/env python3
"""
Скрипт для проверки изменений кнопок выбора пола во всех языках
Использует универсальный TranslationChecker для устранения дублирования кода.
"""

import sys
from pathlib import Path

# Добавляем путь к shared модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.translation_checker import check_gender_buttons

if __name__ == "__main__":
    check_gender_buttons()
