# Debug Info Module

Универсальный модуль для генерации отладочной информации в `shared/metrics/debug_info.py`.

## 🎯 Цель

Централизовать генерацию отладочной информации, убрать дублирование кода и сделать debug-функции переиспользуемыми во всех частях приложения.

## 📦 Что включено

### Основные функции:

1. **`get_user_debug_info(user_id, user, cached_user)`** - Полная информация о пользователе
2. **`get_subscription_debug_info(user_id, status, expires_at)`** - Информация о подписке  
3. **`get_personality_debug_info(user_id, profile)`** - Анализ профиля личности
4. **`get_general_debug_info(title, data)`** - Общая отладочная информация
5. **`get_error_debug_info(error, context)`** - Информация об ошибках

### Класс `DebugInfoGenerator`:

Предоставляет статические методы для более детальной настройки отладочной информации.

## 🚀 Использование

### Простое использование:

```python
from shared.metrics.debug_info import get_user_debug_info

# В обработчике команды
user = await user_service.get_user(user_id)
debug_info = get_user_debug_info(user_id, user, cached_user)
await message.answer(debug_info)
```

### Расширенное использование:

```python
from shared.metrics.debug_info import debug_info_generator

# Кастомная отладочная информация
debug_info = debug_info_generator.format_general_debug_info(
    "Статус системы", 
    {"status": "running", "users": 1000}
)
```

## 📊 Что показывает

### Информация о пользователе:
- ✅ Данные из БД (ID, username, подписка, согласие, etc.)
- ✅ Данные из кэша (для сравнения)
- ✅ Профиль личности (если есть)
- ✅ Даты создания и обновления

### Информация о подписке:
- ✅ Статус подписки
- ✅ Дата истечения
- ✅ Активна ли подписка

### Информация о личности:
- ✅ Количество черт
- ✅ Топ-5 доминирующих черт
- ✅ Значения черт с точностью до 2 знаков

## 🔧 Интеграция

Модуль уже интегрирован в:
- ✅ `app/domain/user/handlers.py` - команда debug
- ✅ `shared/metrics/__init__.py` - экспорт функций

## 📝 Примеры

Смотрите `examples/debug_info_usage.py` для подробных примеров использования.

## 🎨 Форматирование

Все функции возвращают красиво отформатированные строки с эмодзи и структурированной информацией, готовые для отправки в Telegram.

## 🔄 Миграция

Старый код:
```python
debug_info = f"🔍 Debug информация для пользователя {user_id}:\n\n"
if user:
    debug_info += f"📊 Данные из БД:\n"
    # ... много строк кода
```

Новый код:
```python
debug_info = get_user_debug_info(user_id, user, cached_user)
```

**Результат:** Код стал в 10 раз короче и более читаемым! 🎉
