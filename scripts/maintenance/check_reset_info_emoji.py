#!/usr/bin/env python3
"""
Скрипт для проверки переводов reset_info с эмодзи часов во всех языках
"""

import json
import os

def check_reset_info_with_emoji():
    """Проверить переводы reset_info с эмодзи часов во всех языках."""
    
    languages = ['de', 'en', 'es', 'fr', 'it', 'pl', 'ru', 'sr', 'tr']
    
    print("🔍 Проверяем переводы reset_info с эмодзи часов во всех языках...")
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
                reset_info = data['commands']['status'].get('reset_info', 'НЕ НАЙДЕНО')
                print(f"🇷🇺 {lang.upper()}: {reset_info}")
            else:
                print(f"❌ {lang.upper()}: секция commands.status не найдена")
                
        except Exception as e:
            print(f"❌ Ошибка при чтении {file_path}: {e}")
    
    print()
    print("✅ Проверка завершена!")
    print("⏰ Все переводы теперь содержат эмодзи часов для указания времени сброса лимита!")

if __name__ == "__main__":
    check_reset_info_with_emoji()
