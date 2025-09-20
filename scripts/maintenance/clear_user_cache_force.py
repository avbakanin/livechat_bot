#!/usr/bin/env python3
"""
Скрипт для принудительной очистки кэша пользователя через код
"""

import asyncio
import sys
import os

# Добавить путь к проекту
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

from app.shared.fsm.user_cache import user_cache


async def clear_user_cache():
    """Очистить кэш пользователя 627875032."""
    
    user_id = 627875032
    
    print(f"🧹 Очищаем кэш пользователя {user_id}...")
    
    try:
        # Очистить кэш пользователя
        await user_cache.invalidate(user_id)
        print(f"✅ Кэш пользователя {user_id} очищен!")
        
        # Проверить, что кэш действительно очищен
        cached_data = await user_cache.get(user_id)
        if cached_data is None:
            print("✅ Подтверждено: кэш очищен")
        else:
            print("⚠️ Кэш не очищен, попробуйте еще раз")
            
        print("\n🎯 Теперь попробуйте команду /status в боте!")
        print("📝 Кэш очищен, премиум статус должен работать.")
        
    except Exception as e:
        print(f"❌ Ошибка при очистке кэша: {e}")


if __name__ == "__main__":
    asyncio.run(clear_user_cache())
