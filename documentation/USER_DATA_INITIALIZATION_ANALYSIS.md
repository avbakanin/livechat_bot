# 🔄 Анализ загрузки данных пользователя при инициализации

## 📋 Ответ на вопрос

**НЕТ, при инициализации НЕ берутся все данные пользователя в состояние.** Система использует **ленивую загрузку (lazy loading)** - данные загружаются только при первом обращении к ним.

## 🏗️ Архитектура системы кэширования

### **1. Структура данных в кэше (`UserCacheData`):**

```python
@dataclass
class UserCacheData:
    # Основная информация пользователя
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    # Часто используемые данные
    consent_given: bool = False
    gender_preference: str = "female"
    subscription_status: str = "free"
    subscription_expires_at: Optional[datetime] = None
    
    # Счетчик сообщений за день
    daily_message_count: int = 0
    last_message_date: str = ""
    
    # Состояния команд
    is_restarted: bool = False
    is_stopped: bool = False
    
    # Метаданные кэша
    cached_at: datetime
    last_accessed: datetime
```

### **2. Параметры кэша:**
- **TTL (время жизни):** 30 минут
- **Максимальный размер:** 10,000 пользователей
- **Очистка:** каждые 5 минут (автоматическая)

## 🔄 Процесс загрузки данных

### **Этап 1: Middleware (FSM Middleware)**
```python
# app/shared/fsm/fsm_middleware.py
async def __call__(self, handler, event, data):
    user_id = event.from_user.id
    
    # Пытаемся получить данные из кэша
    cached_data = await user_cache.get(user_id)
    
    if cached_data:
        # Данные есть в кэше - используем их
        data["cached_user"] = cached_data
    else:
        # Данных нет в кэше - handlers загрузят из БД
        data["cached_user"] = None
```

### **Этап 2: Первое обращение к данным**
```python
# app/domain/user/services_cached.py
async def get_user_with_cache(self, user_id: int):
    # Пытаемся получить из кэша
    cached_data = await user_cache.get(user_id)
    if cached_data:
        return cached_data  # Данные уже в кэше
    
    # Загружаем из базы данных
    user = await db_get_user(self.pool, user_id)
    if user:
        # Создаем кэш-объект и сохраняем
        cached_data = UserCacheData.from_user(user)
        await user_cache.set(user_id, cached_data)
        return cached_data
```

## 📊 Что загружается из базы данных

### **Полный запрос к БД:**
```sql
SELECT id, username, first_name, last_name, gender_preference,
       subscription_status, consent_given, subscription_expires_at,
       created_at, updated_at
FROM users
WHERE id = $1
```

### **Структура таблицы `users`:**
```sql
CREATE TABLE public.users (
    id BIGINT NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    gender_preference TEXT DEFAULT NULL,
    language TEXT DEFAULT 'en',
    subscription_status TEXT DEFAULT 'free',
    consent_given BOOLEAN DEFAULT FALSE,
    subscription_expires_at TIMESTAMP,
    personality_profile JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT users_pkey PRIMARY KEY (id)
);
```

## ⚡ Стратегия ленивой загрузки

### **Что НЕ загружается при инициализации:**

1. **❌ История сообщений** - загружается только при необходимости
2. **❌ Профиль личности** - загружается при обращении к personality_profile
3. **❌ Языковые настройки** - загружаются отдельно через i18n
4. **❌ Счетчики сообщений** - обновляются по требованию

### **Что загружается при первом обращении:**

1. **✅ Основные данные пользователя** (id, username, names)
2. **✅ Предпочтения** (gender_preference)
3. **✅ Статус подписки** (subscription_status, expires_at)
4. **✅ Согласие** (consent_given)
5. **✅ Временные метки** (created_at, updated_at)

## 🎯 Примеры загрузки данных

### **Сценарий 1: Новый пользователь**
```
1. Пользователь отправляет /start
2. FSM Middleware: cached_data = None
3. cmd_start: проверяет user_exists = False
4. Создает пользователя в БД
5. Данные НЕ кэшируются (новый пользователь)
```

### **Сценарий 2: Существующий пользователь**
```
1. Пользователь отправляет сообщение
2. FSM Middleware: cached_data = None (первый раз)
3. handle_message: обращается к user_service.get_user_with_cache()
4. Загружает данные из БД
5. Сохраняет в кэш на 30 минут
6. Последующие запросы используют кэш
```

### **Сценарий 3: Активный пользователь**
```
1. Пользователь отправляет сообщение
2. FSM Middleware: cached_data = UserCacheData (из кэша)
3. handle_message: использует cached_data напрямую
4. НЕТ обращения к БД
```

## 🔧 Управление кэшем

### **Автоматическая очистка:**
```python
async def _cleanup_loop(self):
    while True:
        await asyncio.sleep(300)  # Каждые 5 минут
        await self._cleanup_expired()  # Удаляет устаревшие записи
```

### **Ручное управление:**
```python
# Инвалидация кэша
await user_cache.invalidate(user_id)

# Обновление поля
await user_cache.update_field(user_id, "subscription_status", "premium")

# Очистка всего кэша
await user_cache.clear()
```

## 📈 Преимущества такой архитектуры

### **1. Производительность:**
- ✅ **Быстрый отклик** - данные в памяти
- ✅ **Меньше нагрузки на БД** - кэширование на 30 минут
- ✅ **Масштабируемость** - до 10,000 активных пользователей

### **2. Экономия ресурсов:**
- ✅ **Память** - загружаются только нужные данные
- ✅ **Сеть** - меньше запросов к БД
- ✅ **CPU** - меньше обработки SQL-запросов

### **3. Гибкость:**
- ✅ **Автоматическое обновление** - TTL 30 минут
- ✅ **Инвалидация** - можно принудительно обновить
- ✅ **Селективная загрузка** - только при необходимости

## 🚨 Ограничения

### **1. Потенциальные проблемы:**
- ⚠️ **Устаревшие данные** - до 30 минут задержки
- ⚠️ **Память** - до 10,000 пользователей в RAM
- ⚠️ **Сложность** - нужно следить за инвалидацией

### **2. Обход ограничений:**
```python
# Принудительное обновление критических данных
await user_cache.update_field(user_id, "subscription_status", new_status)

# Инвалидация при важных изменениях
await user_cache.invalidate(user_id)
```

## 📝 Заключение

**Система НЕ загружает все данные пользователя при инициализации**, а использует **умную стратегию ленивой загрузки**:

- 🎯 **Первое обращение** → загрузка из БД + сохранение в кэш
- ⚡ **Последующие обращения** → использование кэша
- 🕐 **Автоматическая очистка** → каждые 5 минут
- 🔄 **Обновление** → при необходимости или через 30 минут

**Это оптимальное решение** для баланса между производительностью и актуальностью данных! 🚀
