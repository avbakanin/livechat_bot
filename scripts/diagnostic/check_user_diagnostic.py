#!/usr/bin/env python3
"""
Диагностический скрипт для проверки пользователя 627875032
"""

import asyncio
from datetime import datetime

import asyncpg


async def check_user_status():
    """Проверить статус пользователя в базе данных."""
    
    # Подключение к базе данных
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="livechat_bot"
    )
    
    try:
        # Проверить, существует ли пользователь
        user_row = await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1",
            627875032
        )
        
        if not user_row:
            print("❌ Пользователь 627875032 не найден в базе данных!")
            print("Создаем пользователя...")
            
            # Создать пользователя с премиум статусом
            await conn.execute("""
                INSERT INTO users (
                    id, username, first_name, subscription_status, 
                    subscription_expires_at, consent_given
                ) VALUES (
                    $1, $2, $3, $4, $5, $6
                )
            """, 
                627875032, 
                "test_user", 
                "Test User", 
                "premium", 
                datetime.utcnow().replace(microsecond=0) + timedelta(days=120),  # 4 месяца
                True
            )
            
            print("✅ Пользователь создан с премиум статусом!")
            
        else:
            print("✅ Пользователь найден в базе данных:")
            print(f"  ID: {user_row['id']}")
            print(f"  Username: {user_row['username']}")
            print(f"  First Name: {user_row['first_name']}")
            print(f"  Subscription Status: {user_row['subscription_status']}")
            print(f"  Subscription Expires At: {user_row['subscription_expires_at']}")
            print(f"  Consent Given: {user_row['consent_given']}")
            
            # Проверить, активна ли подписка
            if user_row['subscription_status'] == 'premium' and user_row['subscription_expires_at']:
                expires_at = user_row['subscription_expires_at']
                now = datetime.utcnow()
                
                if expires_at > now:
                    days_remaining = (expires_at - now).days
                    hours_remaining = (expires_at - now).seconds // 3600
                    print(f"  ✅ Премиум подписка активна!")
                    print(f"  ⏰ Осталось: {days_remaining} дней, {hours_remaining} часов")
                else:
                    print(f"  ❌ Премиум подписка истекла!")
                    print(f"  ⏰ Истекла: {now - expires_at} назад")
            else:
                print(f"  ❌ Премиум подписка не активна!")
                
        # Проверить кэш пользователя
        print("\n🔍 Проверяем кэш пользователя...")
        cache_row = await conn.fetchrow(
            "SELECT * FROM user_cache WHERE user_id = $1",
            627875032
        )
        
        if cache_row:
            print("✅ Пользователь найден в кэше:")
            print(f"  Subscription Status: {cache_row['subscription_status']}")
            print(f"  Subscription Expires At: {cache_row['subscription_expires_at']}")
        else:
            print("❌ Пользователь не найден в кэше!")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    from datetime import timedelta
    asyncio.run(check_user_status())
