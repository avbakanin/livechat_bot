#!/usr/bin/env python3
"""
Скрипт для исправления премиум подписки пользователя 627875032
Устанавливает правильные данные в БД
"""

import asyncio
from datetime import datetime, timedelta

import asyncpg


async def fix_premium_subscription():
    """Исправить премиум подписку пользователя в БД."""
    
    # Подключение к базе данных
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="livechat_bot"
    )
    
    try:
        user_id = 627875032
        
        print("🔍 Проверяем текущее состояние пользователя...")
        
        # 1. Проверить текущее состояние в БД
        user_row = await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1",
            user_id
        )
        
        if not user_row:
            print(f"❌ Пользователь {user_id} не найден!")
            return
            
        print("✅ Пользователь найден в БД:")
        print(f"  ID: {user_row['id']}")
        print(f"  Username: {user_row['username']}")
        print(f"  Subscription Status: {user_row['subscription_status']}")
        print(f"  Subscription Expires At: {user_row['subscription_expires_at']}")
        
        # 2. Исправить данные в БД
        print("\n🔄 Исправляем данные в БД...")
        
        # Установить дату истечения через 4 месяца
        expires_at = datetime.utcnow().replace(microsecond=0) + timedelta(days=120)
        
        await conn.execute("""
            UPDATE users 
            SET 
                subscription_status = 'premium',
                subscription_expires_at = $1,
                consent_given = TRUE,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = $2
        """, expires_at, user_id)
        
        print(f"✅ Данные в БД обновлены!")
        print(f"  Статус: premium")
        print(f"  Истекает: {expires_at}")
        print(f"  Дней до истечения: {(expires_at - datetime.utcnow()).days}")
        
        # 3. Проверить результат
        print("\n📊 Проверяем результат...")
        updated_row = await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1",
            user_id
        )
        
        if updated_row:
            expires_at = updated_row['subscription_expires_at']
            now = datetime.utcnow()
            
            print(f"  Subscription Status: {updated_row['subscription_status']}")
            print(f"  Subscription Expires At: {updated_row['subscription_expires_at']}")
            
            if updated_row['subscription_status'] == 'premium' and expires_at and expires_at > now:
                days_remaining = (expires_at - now).days
                hours_remaining = (expires_at - now).seconds // 3600
                print(f"  ✅ Премиум подписка активна!")
                print(f"  ⏰ Осталось: {days_remaining} дней, {hours_remaining} часов")
            else:
                print(f"  ❌ Премиум подписка не активна!")
                
        print("\n🎯 Теперь попробуйте команду /status в боте!")
        print("📝 Данные в БД исправлены, премиум статус должен работать.")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(fix_premium_subscription())
