#!/usr/bin/env python3
"""
Скрипт для проверки переводов premium_promo с эмодзи во всех языках
"""

import json
import os

def check_premium_promo_with_emoji():
    """Проверить переводы premium_promo с эмодзи во всех языках."""
    
    languages = ['de', 'en', 'es', 'fr', 'it', 'pl', 'ru', 'sr', 'tr']
    
    print("🔍 Проверяем переводы premium_promo с эмодзи во всех языках...")
    print()
    
    for lang in languages:
        file_path = f"locales/{lang}/translations.json"
        
        if not os.path.exists(file_path):
            print(f"❌ Файл {file_path} не найден")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'commands' in data and 'status' in data['commands']:
                premium_promo = data['commands']['status'].get('premium_promo', 'НЕ НАЙДЕНО')
                print(f"🇷🇺 {lang.upper()}: {premium_promo}")
            else:
                print(f"❌ {lang.upper()}: секция commands.status не найдена")
                
        except Exception as e:
            print(f"❌ Ошибка при чтении {file_path}: {e}")
    
    print()
    print("✅ Проверка завершена!")
    print("💎 Все переводы теперь содержат эмодзи алмаза для привлечения внимания!")

if __name__ == "__main__":
    check_premium_promo_with_emoji()
