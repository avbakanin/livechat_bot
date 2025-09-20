#!/usr/bin/env python3
"""
Скрипт для очистки кэша пользователя 627875032
Этот скрипт поможет решить проблему с премиум статусом
"""

import asyncio
from datetime import datetime, timedelta

import asyncpg


async def clear_user_cache_and_fix_premium():
    """Очистить кэш пользователя и исправить премиум подписку."""
    
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
        
        # 2. Исправить данные в БД если нужно
        print("\n🔄 Проверяем и исправляем данные в БД...")
        
        needs_update = False
        expires_at = None
        
        if user_row['subscription_status'] != 'premium':
            print("  ⚠️ Статус подписки не 'premium', исправляем...")
            needs_update = True
            
        if not user_row['subscription_expires_at']:
            print("  ⚠️ Дата истечения подписки не установлена, исправляем...")
            needs_update = True
            expires_at = datetime.utcnow().replace(microsecond=0) + timedelta(days=120)
        elif user_row['subscription_expires_at'] <= datetime.utcnow():
            print("  ⚠️ Подписка истекла, продлеваем...")
            needs_update = True
            expires_at = datetime.utcnow().replace(microsecond=0) + timedelta(days=120)
        else:
            expires_at = user_row['subscription_expires_at']
            
        if needs_update:
            await conn.execute("""
                UPDATE users 
                SET 
                    subscription_status = 'premium',
                    subscription_expires_at = $1,
                    consent_given = TRUE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
            """, expires_at, user_id)
            
            print(f"  ✅ Данные в БД обновлены!")
            print(f"  Статус: premium")
            print(f"  Истекает: {expires_at}")
        else:
            print("  ✅ Данные в БД корректны!")
            
        # 3. Очистить кэш пользователя (если есть таблица кэша)
        print("\n🧹 Очищаем кэш пользователя...")
        try:
            # Попробовать удалить из кэша
            result = await conn.execute(
                "DELETE FROM user_cache WHERE user_id = $1",
                user_id
            )
            print(f"  ✅ Кэш очищен: {result}")
        except Exception as e:
            print(f"  ⚠️ Не удалось очистить кэш (возможно, таблица не существует): {e}")
            
        # 4. Проверить финальный результат
        print("\n📊 Финальная проверка...")
        final_row = await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1",
            user_id
        )
        
        if final_row:
            expires_at = final_row['subscription_expires_at']
            now = datetime.utcnow()
            
            print(f"  Subscription Status: {final_row['subscription_status']}")
            print(f"  Subscription Expires At: {final_row['subscription_expires_at']}")
            
            if final_row['subscription_status'] == 'premium' and expires_at and expires_at > now:
                days_remaining = (expires_at - now).days
                hours_remaining = (expires_at - now).seconds // 3600
                print(f"  ✅ Премиум подписка активна!")
                print(f"  ⏰ Осталось: {days_remaining} дней, {hours_remaining} часов")
            else:
                print(f"  ❌ Премиум подписка не активна!")
                
        print("\n🎯 Теперь попробуйте команду /status в боте!")
        print("📝 Кэш очищен, премиум статус должен работать корректно.")
        print("\n💡 Если проблема остается:")
        print("   1. Перезапустите бота")
        print("   2. Или подождите 30 минут (время жизни кэша)")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(clear_user_cache_and_fix_premium())
