#!/usr/bin/env python3
"""
Универсальные утилиты для работы с базой данных в скриптах.
Устраняет дублирование кода подключения к БД.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

import asyncpg
from dotenv import load_dotenv


class DatabaseConnection:
    """Класс для управления подключением к базе данных."""
    
    def __init__(self):
        """Инициализация с загрузкой переменных окружения."""
        load_dotenv()
        self.connection: Optional[asyncpg.Connection] = None
    
    async def connect(self) -> asyncpg.Connection:
        """Подключиться к базе данных."""
        if self.connection is None or self.connection.is_closed():
            self.connection = await asyncpg.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "5432")),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "postgres"),
                database=os.getenv("DB_NAME", "livechat_bot")
            )
        return self.connection
    
    async def close(self):
        """Закрыть подключение к базе данных."""
        if self.connection and not self.connection.is_closed():
            await self.connection.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self.connection
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


class UserManager:
    """Менеджер для работы с пользователями."""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    async def get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить информацию о пользователе."""
        async with self.db as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1",
                user_id
            )
            return dict(row) if row else None
    
    async def update_user_subscription(
        self, 
        user_id: int, 
        status: str = "premium",
        days_duration: int = 120
    ) -> bool:
        """Обновить подписку пользователя."""
        async with self.db as conn:
            expires_at = datetime.utcnow().replace(microsecond=0) + timedelta(days=days_duration)
            
            result = await conn.execute("""
                UPDATE users 
                SET 
                    subscription_status = $1,
                    subscription_expires_at = $2,
                    consent_given = TRUE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = $3
            """, status, expires_at, user_id)
            
            return "UPDATE 1" in result
    
    async def clear_user_cache(self, user_id: int) -> bool:
        """Очистить кэш пользователя."""
        async with self.db as conn:
            try:
                await conn.execute(
                    "DELETE FROM user_cache WHERE user_id = $1",
                    user_id
                )
                return True
            except Exception:
                return False
    
    async def print_user_status(self, user_id: int):
        """Вывести статус пользователя."""
        user_info = await self.get_user_info(user_id)
        
        if not user_info:
            print(f"❌ Пользователь {user_id} не найден!")
            return
        
        print(f"✅ Пользователь найден:")
        print(f"  ID: {user_info['id']}")
        print(f"  Username: {user_info['username']}")
        print(f"  Subscription Status: {user_info['subscription_status']}")
        print(f"  Subscription Expires At: {user_info['subscription_expires_at']}")
        print(f"  Consent Given: {user_info['consent_given']}")
        
        # Проверить активность подписки
        expires_at = user_info['subscription_expires_at']
        if expires_at:
            now = datetime.utcnow()
            if expires_at > now:
                days_remaining = (expires_at - now).days
                hours_remaining = (expires_at - now).seconds // 3600
                print(f"  ✅ Премиум подписка активна!")
                print(f"  ⏰ Осталось: {days_remaining} дней, {hours_remaining} часов")
            else:
                print(f"  ❌ Премиум подписка истекла!")


class PremiumFixer:
    """Класс для исправления премиум подписки."""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self.user_manager = UserManager(db_connection)
    
    async def fix_user_premium(self, user_id: int, days_duration: int = 120) -> bool:
        """Исправить премиум подписку пользователя."""
        print(f"🔍 Исправляем премиум подписку для пользователя {user_id}...")
        
        # Показать текущее состояние
        await self.user_manager.print_user_status(user_id)
        
        # Обновить подписку
        print(f"\n🔄 Обновляем подписку на {days_duration} дней...")
        success = await self.user_manager.update_user_subscription(user_id, days_duration=days_duration)
        
        if success:
            print("✅ Подписка обновлена!")
            
            # Очистить кэш
            print("\n🧹 Очищаем кэш...")
            cache_cleared = await self.user_manager.clear_user_cache(user_id)
            if cache_cleared:
                print("✅ Кэш очищен!")
            else:
                print("⚠️ Кэш не очищен (возможно, таблица не существует)")
            
            # Показать финальный статус
            print("\n📊 Финальный статус:")
            await self.user_manager.print_user_status(user_id)
            
            print("\n🎯 Теперь попробуйте команду /status в боте!")
            return True
        else:
            print("❌ Не удалось обновить подписку!")
            return False


# Удобные функции для обратной совместимости
async def fix_premium_subscription(user_id: int = 627875032, days_duration: int = 120):
    """Исправить премиум подписку пользователя."""
    db = DatabaseConnection()
    fixer = PremiumFixer(db)
    
    try:
        await fixer.fix_user_premium(user_id, days_duration)
    finally:
        await db.close()


async def clear_user_cache(user_id: int = 627875032):
    """Очистить кэш пользователя."""
    db = DatabaseConnection()
    user_manager = UserManager(db)
    
    try:
        print(f"🧹 Очищаем кэш пользователя {user_id}...")
        
        # Обновить данные в БД
        print("🔄 Обновляем данные в БД...")
        await user_manager.update_user_subscription(user_id)
        
        # Очистить кэш
        cache_cleared = await user_manager.clear_user_cache(user_id)
        if cache_cleared:
            print("✅ Кэш очищен!")
        else:
            print("⚠️ Кэш не очищен (возможно, таблица не существует)")
        
        # Показать финальный статус
        print("\n📊 Финальный статус:")
        await user_manager.print_user_status(user_id)
        
        print("\n🎯 Теперь попробуйте команду /status в боте!")
        
    finally:
        await db.close()


async def clear_user_cache_force(user_id: int = 627875032):
    """Принудительно очистить кэш пользователя через код."""
    # Добавить путь к проекту
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    try:
        from app.shared.fsm.user_cache import user_cache
        
        print(f"🧹 Принудительно очищаем кэш пользователя {user_id}...")
        
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
        
    except ImportError as e:
        print(f"❌ Не удалось импортировать user_cache: {e}")
    except Exception as e:
        print(f"❌ Ошибка при очистке кэша: {e}")


if __name__ == "__main__":
    # Демонстрация использования
    async def demo():
        print("=== Демонстрация DatabaseUtils ===")
        print()
        
        # Исправить премиум подписку
        await fix_premium_subscription()
        print()
        
        # Очистить кэш
        await clear_user_cache()
        print()
        
        # Принудительно очистить кэш
        await clear_user_cache_force()
    
    asyncio.run(demo())
