#!/usr/bin/env python3
"""
Скрипт для проверки переводов кнопки extend_premium во всех языках
"""

import json
import os

def check_translations():
    """Проверить переводы во всех языках."""
    
    languages = ['de', 'en', 'es', 'fr', 'it', 'pl', 'ru', 'sr', 'tr']
    missing_translations = []
    
    print("🔍 Проверяем переводы для кнопки 'extend_premium'...")
    
    for lang in languages:
        file_path = f"locales/{lang}/translations.json"
        
        if not os.path.exists(file_path):
            print(f"❌ Файл {file_path} не найден")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'buttons' in data and 'extend_premium' in data['buttons']:
                translation = data['buttons']['extend_premium']
                print(f"✅ {lang.upper()}: {translation}")
            else:
                missing_translations.append(lang)
                print(f"❌ {lang.upper()}: перевод отсутствует")
                
        except Exception as e:
            print(f"❌ Ошибка при чтении {file_path}: {e}")
    
    print(f"\n📊 Результат проверки:")
    print(f"✅ Переведено: {len(languages) - len(missing_translations)}/{len(languages)}")
    
    if missing_translations:
        print(f"❌ Отсутствуют переводы для: {', '.join(missing_translations)}")
    else:
        print("🎉 Все переводы добавлены корректно!")

if __name__ == "__main__":
    check_translations()
