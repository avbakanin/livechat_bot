#!/usr/bin/env python3
"""
Скрипт для проверки изменений кнопок выбора пола во всех языках
"""

import json
import os

def check_gender_buttons():
    """Проверить кнопки выбора пола во всех языках."""
    
    languages = ['de', 'en', 'es', 'fr', 'it', 'pl', 'ru', 'sr', 'tr']
    
    print("🔍 Проверяем кнопки выбора пола во всех языках...")
    print()
    
    for lang in languages:
        file_path = f"locales/{lang}/translations.json"
        
        if not os.path.exists(file_path):
            print(f"❌ Файл {file_path} не найден")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'buttons' in data:
                choose_female = data['buttons'].get('choose_female', 'НЕ НАЙДЕНО')
                choose_male = data['buttons'].get('choose_male', 'НЕ НАЙДЕНО')
                
                print(f"🇷🇺 {lang.upper()}:")
                print(f"  Девушка: {choose_female}")
                print(f"  Мужчина: {choose_male}")
                print()
                
        except Exception as e:
            print(f"❌ Ошибка при чтении {file_path}: {e}")
    
    print("✅ Проверка завершена!")

if __name__ == "__main__":
    check_gender_buttons()
