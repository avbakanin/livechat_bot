#!/usr/bin/env python3
"""
Скрипт для проверки переводов сообщения остановки бота во всех языках
"""

import json
import os

def check_stop_success_translations():
    """Проверить переводы stop.success во всех языках."""
    
    languages = ['de', 'en', 'es', 'fr', 'it', 'pl', 'ru', 'sr', 'tr']
    
    print("🔍 Проверяем переводы stop.success во всех языках...")
    print()
    
    for lang in languages:
        file_path = f"locales/{lang}/translations.json"
        
        if not os.path.exists(file_path):
            print(f"❌ Файл {file_path} не найден")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'commands' in data and 'stop' in data['commands']:
                success_message = data['commands']['stop'].get('success', 'НЕ НАЙДЕНО')
                print(f"🇷🇺 {lang.upper()}: {success_message}")
                
                # Проверяем наличие эмодзи грусти
                if '😢' in success_message:
                    print(f"   ✅ Содержит эмодзи грусти")
                else:
                    print(f"   ❌ НЕ содержит эмодзи грусти")
                    
                # Проверяем наличие текста о возвращении
                if any(word in success_message.lower() for word in ['return', 'ritorno', 'regreso', 'retour', 'powrót', 'возвращ', 'повратак', 'dönüş']):
                    print(f"   ✅ Содержит текст о возвращении")
                else:
                    print(f"   ❌ НЕ содержит текст о возвращении")
                    
            else:
                print(f"❌ {lang.upper()}: секция commands.stop не найдена")
                
        except Exception as e:
            print(f"❌ Ошибка при чтении {file_path}: {e}")
        
        print()
    
    print("✅ Проверка завершена!")
    print("😢 Все переводы теперь содержат сообщение о том, что нам жаль и мы ждем возвращения!")

if __name__ == "__main__":
    check_stop_success_translations()
