# 🔄 Анализ команды /restart

## 📋 Как работает команда /restart

### 1. **Инициация команды**
```python
@router.message(Command(commands=[BotCommands.RESTART]))
async def cmd_restart(message: Message, i18n: I18nMiddleware, cached_user: UserCacheData = None):
```

**Что происходит:**
- Пользователь отправляет команду `/restart`
- Проверяется флаг `cached_user.is_restarted` - если бот уже перезапущен, показывается предупреждение
- Если не перезапущен, показывается диалог подтверждения

### 2. **Диалог подтверждения**
```html
🔄 Перезапуск бота

Вы уверены, что хотите перезапустить бота?

Все ваши данные будут удалены:
• История переписки
• Настройки  
• Кэш

Пожалуйста, подтвердите действие.
```

**Кнопки:**
- ✅ **Да** (`restart_confirm`)
- ❌ **Нет** (`restart_cancel`)

### 3. **Подтверждение и выполнение**
```python
async def restart_confirm(callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware):
    await user_service.restart_user_state(user_id)
```

## 🗄️ Что удаляется из базы данных

### **Функция `restart_user_state(user_id)`:**
```python
async def restart_user_state(self, user_id: int) -> None:
    """Restart user state - clear messages but keep consent and go to gender selection."""
```

### **1. Удаление всех сообщений**
```sql
DELETE FROM messages WHERE user_id = $1
```
- **Таблица:** `messages`
- **Что удаляется:** ВСЕ сообщения пользователя (история переписки)
- **Функция:** `delete_user_messages(user_id)`

### **2. Сброс предпочтения пола**
```sql
UPDATE users SET gender_preference = NULL WHERE id = $1
```
- **Таблица:** `users`
- **Поле:** `gender_preference`
- **Что происходит:** Устанавливается в `NULL`
- **Функция:** `clear_gender_preference(user_id)`

### **3. Сброс профиля личности**
```sql
UPDATE users SET personality_profile = NULL WHERE id = $1
```
- **Таблица:** `users`
- **Поле:** `personality_profile` (JSONB)
- **Что происходит:** Устанавливается в `NULL`
- **Функция:** `clear_personality_profile(user_id)`

### **4. Очистка кэша**
```python
await self.invalidate_cache(user_id)
```
- **Что происходит:** Удаление всех данных пользователя из кэша FSM
- **Результат:** Следующий запрос загрузит свежие данные из БД

## 🔒 Что НЕ удаляется

### **Сохраненные данные:**
1. **Согласие на обработку данных** (`consent_given`) - остается `TRUE`
2. **Подписка** (`subscription_status`, `subscription_expires_at`) - не изменяется
3. **Язык** (`language`) - остается прежним
4. **Основные данные пользователя** (`username`, `first_name`, `last_name`)
5. **Дата создания** (`created_at`) - не изменяется
6. **Дата обновления** (`updated_at`) - не изменяется

## 📊 Структура таблиц

### **Таблица `users`:**
```sql
CREATE TABLE public.users (
    id BIGINT NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    gender_preference TEXT DEFAULT NULL,        -- ← Сбрасывается в NULL
    language TEXT DEFAULT 'en',                 -- ← Сохраняется
    subscription_status TEXT DEFAULT 'free',    -- ← Сохраняется
    consent_given BOOLEAN DEFAULT FALSE,        -- ← Сохраняется
    subscription_expires_at TIMESTAMP,          -- ← Сохраняется
    personality_profile JSONB,                  -- ← Сбрасывается в NULL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT users_pkey PRIMARY KEY (id)
);
```

### **Таблица `messages` (партиционированная):**
```sql
CREATE TABLE public.messages (
    id BIGSERIAL NOT NULL,
    user_id BIGINT NOT NULL,
    role TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT messages_pkey PRIMARY KEY (id, created_at),
    CONSTRAINT messages_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
) PARTITION BY RANGE (created_at);
```
**Удаляются:** ВСЕ записи с `user_id = $1`

## 🎯 Последовательность действий после restart

### **1. Обновление кэша:**
```python
cached_data.is_restarted = True
cached_data.is_stopped = False  # Reset stop state
await user_cache.set(user_id, cached_data)
```

### **2. Сообщение об успехе:**
```
✅ Бот перезапущен!

Все данные очищены. Начинаем заново...
```

### **3. Переход к выбору пола:**
```python
await asyncio.sleep(2)
await callback.message.answer(
    text=i18n.t("gender.choose_gender"),
    reply_markup=get_gender_keyboard(),
    parse_mode="HTML"
)
```

## ⚠️ Важные особенности

### **1. Защита от повторного запуска:**
- Проверка флага `is_restarted` в кэше
- Если уже перезапущен, показывается предупреждение

### **2. Сохранение критичных данных:**
- **Согласие на обработку** - пользователь не должен давать согласие заново
- **Подписка** - премиум статус сохраняется
- **Язык** - настройки языка остаются

### **3. Полная очистка истории:**
- Удаляются ВСЕ сообщения пользователя
- Сбрасывается профиль личности (результаты квиза)
- Сбрасывается выбор пола компаньона

## 🔄 Сравнение с /stop

| Параметр | /restart | /stop |
|----------|----------|-------|
| **Сообщения** | ❌ Удаляются | ❌ Удаляются |
| **Пол компаньона** | ❌ Сбрасывается | ❌ Сбрасывается |
| **Профиль личности** | ❌ Сбрасывается | ❌ Сбрасывается |
| **Согласие** | ✅ Сохраняется | ✅ Сохраняется |
| **Подписка** | ✅ Сохраняется | ✅ Сохраняется |
| **Язык** | ✅ Сохраняется | ✅ Сохраняется |
| **Результат** | Выбор пола | Прощание |

## 📝 Заключение

Команда `/restart` выполняет **мягкий сброс** состояния пользователя:
- **Удаляет:** историю переписки, настройки пола и личности
- **Сохраняет:** согласие, подписку, язык и основные данные
- **Результат:** пользователь возвращается к выбору пола компаньона

Это позволяет начать общение заново, сохранив при этом важные настройки и статус подписки.
