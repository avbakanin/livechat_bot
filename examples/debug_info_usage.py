"""
Пример использования модуля debug_info из shared/metrics.

Этот файл демонстрирует, как использовать новые функции для генерации
отладочной информации в различных частях приложения.
"""

from shared.metrics.debug_info import (
    get_user_debug_info,
    get_subscription_debug_info,
    get_personality_debug_info,
    get_general_debug_info,
    get_error_debug_info,
)


# Пример 1: Отладочная информация о пользователе
async def example_user_debug(user_id: int, user_service, cached_user=None):
    """Пример использования отладочной информации о пользователе."""
    
    # Получаем пользователя из БД
    user = await user_service.get_user(user_id)
    
    # Генерируем отладочную информацию одной строкой
    debug_info = get_user_debug_info(user_id, user, cached_user)
    
    print(debug_info)
    # Вывод:
    # 🔍 Debug информация для пользователя 12345:
    # 
    # 📊 Данные из БД:
    #   ID: 12345
    #   Username: test_user
    #   First Name: Test
    #   Last Name: User
    #   Language: en
    #   Gender Preference: female
    #   Subscription Status: free
    #   Subscription Expires At: None
    #   Consent Given: True
    #   Created At: 2024-01-01 12:00:00
    #   Updated At: 2024-01-01 12:00:00
    # 
    # 💾 Данные из кэша:
    #   Subscription Status: free
    #   Subscription Expires At: None
    #   Consent Given: True
    #   Language: en
    #   Gender Preference: female


# Пример 2: Отладочная информация о подписке
def example_subscription_debug(user_id: int, subscription_status: str, expires_at=None):
    """Пример использования отладочной информации о подписке."""
    
    debug_info = get_subscription_debug_info(user_id, subscription_status, expires_at)
    
    print(debug_info)
    # Вывод:
    # 💳 Debug информация о подписке для пользователя 12345:
    # 
    #   Статус: premium
    #   Истекает: 2024-12-31 23:59:59
    #   Активна: Да


# Пример 3: Отладочная информация о личности
def example_personality_debug(user_id: int, personality_profile=None):
    """Пример использования отладочной информации о личности."""
    
    # Пример профиля личности
    if personality_profile is None:
        personality_profile = {
            "extroverted": 2.5,
            "creative": 2.1,
            "analytical": 1.8,
            "emotional": 1.5,
            "playful": 1.2,
            "direct": 0.8,
            "cautious": 0.5,
            "traditional": 0.3
        }
    
    debug_info = get_personality_debug_info(user_id, personality_profile)
    
    print(debug_info)
    # Вывод:
    # 🧠 Debug информация о личности для пользователя 12345:
    # 
    #   Профиль найден: Да
    #   Количество черт: 8
    # 
    #   Топ-5 черт:
    #     1. extroverted: 2.50
    #     2. creative: 2.10
    #     3. analytical: 1.80
    #     4. emotional: 1.50
    #     5. playful: 1.20
    #     ... и еще 3 черт


# Пример 4: Общая отладочная информация
def example_general_debug():
    """Пример использования общей отладочной информации."""
    
    data = {
        "bot_status": "running",
        "database_connection": "active",
        "cache_status": "healthy",
        "metrics": {
            "total_users": 1000,
            "active_today": 150,
            "messages_processed": 5000
        },
        "features": ["personality", "subscriptions", "multilang"]
    }
    
    debug_info = get_general_debug_info("Статус системы", data)
    
    print(debug_info)
    # Вывод:
    # 🔍 Статус системы:
    # 
    #   bot_status: running
    #   database_connection: active
    #   cache_status: healthy
    #   metrics:
    #     total_users: 1000
    #     active_today: 150
    #     messages_processed: 5000
    #   features: [personality, subscriptions, multilang]


# Пример 5: Отладочная информация об ошибке
def example_error_debug():
    """Пример использования отладочной информации об ошибке."""
    
    try:
        # Симулируем ошибку
        raise ValueError("Тестовая ошибка")
    except Exception as e:
        context = {
            "user_id": 12345,
            "operation": "send_message",
            "timestamp": "2024-01-01 12:00:00"
        }
        
        debug_info = get_error_debug_info(e, context)
        
        print(debug_info)
        # Вывод:
        # ❌ Debug информация об ошибке:
        # 
        #   Тип ошибки: ValueError
        #   Сообщение: Тестовая ошибка
        # 
        #   Контекст:
        #     user_id: 12345
        #     operation: send_message
        #     timestamp: 2024-01-01 12:00:00


# Пример 6: Использование в Telegram боте
async def telegram_bot_example(message, user_service, cached_user=None):
    """Пример использования в обработчике Telegram бота."""
    
    user_id = message.from_user.id
    
    try:
        # Получаем пользователя
        user = await user_service.get_user(user_id)
        
        # Генерируем отладочную информацию
        debug_info = get_user_debug_info(user_id, user, cached_user)
        
        # Отправляем пользователю
        await message.answer(debug_info)
        
    except Exception as e:
        # В случае ошибки генерируем информацию об ошибке
        error_info = get_error_debug_info(e, {"user_id": user_id, "command": "debug"})
        await message.answer(f"❌ Ошибка:\n{error_info}")


if __name__ == "__main__":
    # Запускаем примеры
    print("=== Примеры использования debug_info ===\n")
    
    print("1. Отладочная информация о пользователе:")
    example_user_debug(12345, None)
    
    print("\n2. Отладочная информация о подписке:")
    example_subscription_debug(12345, "premium")
    
    print("\n3. Отладочная информация о личности:")
    example_personality_debug(12345)
    
    print("\n4. Общая отладочная информация:")
    example_general_debug()
    
    print("\n5. Отладочная информация об ошибке:")
    example_error_debug()
