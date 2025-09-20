#!/usr/bin/env python3
"""
Скрипт для перезапуска бота и очистки кэша в памяти
"""

import subprocess
import sys
import os
import time


def restart_bot():
    """Перезапустить бота для очистки кэша в памяти."""
    
    print("🔄 Перезапускаем бота для очистки кэша...")
    
    try:
        # Найти процесс бота
        if os.name == 'nt':  # Windows
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
                capture_output=True, text=True
            )
            
            if 'main.py' in result.stdout:
                print("  📋 Найден запущенный бот")
                
                # Остановить бот
                print("  ⏹️ Останавливаем бот...")
                subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                             capture_output=True)
                time.sleep(2)
                
                print("  ✅ Бот остановлен")
            else:
                print("  ℹ️ Бот не запущен")
                
        else:  # Linux/Mac
            result = subprocess.run(
                ['pgrep', '-f', 'main.py'],
                capture_output=True, text=True
            )
            
            if result.stdout.strip():
                print("  📋 Найден запущенный бот")
                
                # Остановить бот
                print("  ⏹️ Останавливаем бот...")
                subprocess.run(['pkill', '-f', 'main.py'])
                time.sleep(2)
                
                print("  ✅ Бот остановлен")
            else:
                print("  ℹ️ Бот не запущен")
        
        # Запустить бот заново
        print("  🚀 Запускаем бот...")
        
        # Перейти в директорию проекта
        project_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.join(project_dir, '..', '..')
        
        if os.name == 'nt':  # Windows
            subprocess.Popen(
                ['python', 'main.py'],
                cwd=project_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:  # Linux/Mac
            subprocess.Popen(
                ['python3', 'main.py'],
                cwd=project_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        print("  ✅ Бот запущен!")
        print("\n🎯 Теперь попробуйте команду /status в боте!")
        print("📝 Кэш в памяти очищен, премиум статус должен работать.")
        
    except Exception as e:
        print(f"❌ Ошибка при перезапуске: {e}")
        print("\n💡 Попробуйте перезапустить бот вручную:")
        print("   1. Остановите бот (Ctrl+C)")
        print("   2. Запустите заново: python main.py")


if __name__ == "__main__":
    restart_bot()
