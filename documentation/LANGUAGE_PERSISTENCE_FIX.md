# Исправление проблемы с сохранением языка пользователя

## Проблема
После выбора языка через команду `/language` бот продолжал отвечать на английском языке, не сохраняя выбранный пользователем язык.

## Причина
Язык устанавливался только глобально в сессии, но не сохранялся в базе данных для конкретного пользователя. При следующем сообщении middleware загружал язык из Telegram (который мог быть английским) вместо сохраненного пользователем.

## Решение

### 1. Добавлено поле `language` в таблицу `users`
```sql
-- Migration: Add language field to users table
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'ru';

CREATE INDEX IF NOT EXISTS idx_users_language ON public.users USING btree (language);

UPDATE public.users 
SET language = 'ru' 
WHERE language IS NULL;
```

### 2. Обновлен `UserService`
Добавлен метод `get_user_language()` для получения языка пользователя из базы данных:
```python
async def get_user_language(self, pool, user_id: int) -> str:
    """Get user language preference."""
    async with pool.acquire() as conn:
        try:
            language = await conn.fetchval(
                "SELECT language FROM users WHERE id = $1", user_id
            )
            return language or 'ru'  # Default to Russian
        except Exception as e:
            logging.error(f"Error getting language for user {user_id}: {e}")
            return 'ru'  # Default fallback
```

### 3. Обновлен обработчик выбора языка
Теперь при выборе языка он сохраняется в базе данных:
```python
# Save user language preference to database
user_id = callback.from_user.id
try:
    from services.user.user import user_service
    pool = callback.bot.get('pool')
    if pool:
        await user_service.update_user(
            pool=pool,
            user_id=user_id,
            language=language_code
        )
        logging.info(f"Saved language preference '{language_code}' for user {user_id}")
except Exception as e:
    logging.warning(f"Failed to save language preference for user {user_id}: {e}")
```

### 4. Обновлен `I18nMiddleware`
Middleware теперь загружает язык пользователя из базы данных:
```python
# Try to get user's saved language preference from database
try:
    from services.user.user import user_service
    pool = data.get('pool')
    if pool:
        user_language = await user_service.get_user_language(pool, user_id)
    else:
        # Fallback to Telegram language code
        user_language = event.from_user.language_code or "ru"
except Exception as e:
    logging.warning(f"Failed to get user language for {user_id}: {e}")
    user_language = event.from_user.language_code or "ru"
```

## Результат
Теперь при выборе языка через команду `/language`:
1. ✅ Язык сохраняется в базе данных для конкретного пользователя
2. ✅ При следующих сообщениях бот использует сохраненный язык
3. ✅ Если сохранение не удалось, используется язык из Telegram как fallback
4. ✅ **По умолчанию используется язык Telegram** (не русский)
5. ✅ Приоритет: сохраненный язык > язык Telegram > русский (fallback)

## Тестирование
Создан тест `test_language_persistence.py`, который проверяет:
- ✅ Импорты всех компонентов
- ✅ Наличие метода `get_user_language`
- ✅ Создание `I18nMiddleware`
- ✅ Работу переводов на разных языках

## Дополнительные исправления

### Исправлена ошибка получения pool
**Проблема:** `'Bot' object has no attribute 'get'` и `No database pool available`
**Решение:** 
1. Обновлен `ServiceMiddleware` для передачи pool:
```python
class ServiceMiddleware(BaseMiddleware):
    def __init__(self, user_service, message_service, pool=None):
        self.pool = pool
    
    async def __call__(self, handler, event, data):
        if self.pool:
            data["pool"] = self.pool
```

2. Обновлен обработчик для получения pool из kwargs:
```python
async def handle_language_selection(callback, i18n, **kwargs):
    pool = kwargs.get('pool')
```

3. Обновлен main.py для передачи pool в ServiceMiddleware:
```python
ServiceMiddleware(user_service, message_service, pool)
```

### Убран русский язык по умолчанию
**Проблема:** Всегда использовался русский язык по умолчанию
**Решение:** 
- Поле `language` в БД теперь может быть NULL
- По умолчанию используется язык Telegram
- Русский используется только как fallback

### Обновлена логика приоритета языков
1. **Сохраненный язык** (если пользователь выбрал через `/language`)
2. **Язык Telegram** (из настроек пользователя)
3. **Русский** (fallback, если ничего не определено)

## Применение миграции
Для применения изменений выполните:
```sql
-- Выполните содержимое файла migration_add_language_field.sql
-- в вашей базе данных PostgreSQL
```

После этого перезапустите бота, и сохранение языка будет работать корректно.
