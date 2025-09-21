#!/usr/bin/env python3
"""
Скрипт для проверки переводов premium_promo во всех языках
Использует универсальный TranslationChecker для устранения дублирования кода.
"""

import sys
from pathlib import Path

# Добавляем путь к shared модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.translation_checker import check_premium_promo, check_premium_promo_with_emoji

if __name__ == "__main__":
    print("=== Проверка переводов premium_promo ===")
    print()
    
    # Обычная проверка
    check_premium_promo()
    print()
    
    # Проверка с эмодзи
    print("=== Проверка переводов premium_promo с эмодзи ===")
    check_premium_promo_with_emoji()
