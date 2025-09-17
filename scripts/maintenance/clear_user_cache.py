#!/usr/bin/env python3
"""
Скрипт для очистки кэша пользователя 627875032
"""

import asyncio
from datetime import datetime, timedelta

import asyncpg


async def clear_user_cache():
    """Очистить кэш пользователя и обновить данные."""
    
    # Подключение к базе данных
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="livechat_bot"
    )
    
    try:
        # 1. Обновить пользователя в базе данных
        print("🔄 Обновляем пользователя в базе данных...")
        await conn.execute("""
            UPDATE users 
            SET 
                subscription_status = 'premium',
                subscription_expires_at = $1,
                consent_given = TRUE,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = $2
        """, 
            datetime.utcnow().replace(microsecond=0) + timedelta(days=120),  # 4 месяца
            627875032
        )
        
        # 2. Проверить результат
        user_row = await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1",
            627875032
        )
        
        if user_row:
            print("✅ Пользователь обновлен в базе данных:")
            print(f"  Subscription Status: {user_row['subscription_status']}")
            print(f"  Subscription Expires At: {user_row['subscription_expires_at']}")
            print(f"  Consent Given: {user_row['consent_given']}")
        else:
            print("❌ Пользователь не найден!")
            return
            
        # 3. Очистить кэш пользователя (если есть таблица кэша)
        print("\n🧹 Очищаем кэш пользователя...")
        try:
            # Попробовать удалить из кэша
            result = await conn.execute(
                "DELETE FROM user_cache WHERE user_id = $1",
                627875032
            )
            print(f"✅ Кэш очищен: {result}")
        except Exception as e:
            print(f"⚠️ Не удалось очистить кэш (возможно, таблица не существует): {e}")
            
        # 4. Проверить финальный статус
        print("\n📊 Финальный статус пользователя:")
        final_row = await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1",
            627875032
        )
        
        if final_row:
            expires_at = final_row['subscription_expires_at']
            now = datetime.utcnow()
            
            if expires_at > now:
                days_remaining = (expires_at - now).days
                hours_remaining = (expires_at - now).seconds // 3600
                print(f"  ✅ Премиум подписка активна!")
                print(f"  ⏰ Осталось: {days_remaining} дней, {hours_remaining} часов")
            else:
                print(f"  ❌ Премиум подписка истекла!")
                
        print("\n🎯 Теперь попробуйте команду /status в боте!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(clear_user_cache())
