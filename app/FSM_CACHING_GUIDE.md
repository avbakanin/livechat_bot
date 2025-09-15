# FSM (Finite State Machine) Caching System

## Обзор

FSM система кеширования была внедрена для оптимизации производительности бота путем уменьшения количества запросов к базе данных. Вместо выполнения 7+ запросов к БД на каждое сообщение пользователя, система теперь кеширует часто используемые данные пользователя в памяти.

## Архитектура

### Компоненты

1. **UserCache** (`app/shared/fsm/user_cache.py`)
   - In-memory кеш с TTL (Time To Live)
   - Автоматическая очистка устаревших данных
   - Ограничение размера кеша
   - Thread-safe операции

2. **FSMMiddleware** (`app/shared/fsm/fsm_middleware.py`)
   - Middleware для автоматического кеширования
   - Инжекция кешированных данных в handlers
   - Обработка cache miss/miss scenarios

3. **CachedUserService** (`app/domain/user/services_cached.py`)
   - Улучшенный UserService с поддержкой кеширования
   - Автоматическое обновление кеша при изменениях
   - Fallback на прямые запросы к БД

## Кешируемые данные

### ✅ Кешируется
- `consent_given` - статус согласия (редко меняется)
- `gender_preference` - предпочтение пола (меняется только по команде)
- `subscription_status` - статус подписки (редко меняется)
- `subscription_expires_at` - дата истечения подписки
- `username`, `first_name`, `last_name` - базовая информация

### ❌ НЕ кешируется
- `messages_today_count` - счетчик сообщений (обновляется при каждом сообщении)
- `chat_history` - история сообщений (может быть большой)

## Конфигурация

### Параметры кеша
```python
# В app/shared/fsm/user_cache.py
ttl_minutes = 30        # Время жизни кеша
max_size = 10000        # Максимальный размер кеша
cleanup_interval = 300  # Интервал очистки (секунды)
```

### Middleware порядок
```python
# В app/main.py
middlewares = [
    I18nMiddleware(),           # 1. Локализация
    FSMMiddleware(),            # 2. Кеширование (раньше AccessMiddleware)
    AccessMiddleware(),         # 3. Контроль доступа
    LoggingMiddleware(),        # 4. Логирование
    ServiceMiddleware(),        # 5. Инжекция сервисов
]
```

## Использование в handlers

### До FSM (7+ запросов к БД)
```python
async def handle_message(message, user_service, ...):
    # 1. add_user() - INSERT/UPDATE
    # 2. get_consent_status() - SELECT
    # 3. can_send_message() - SELECT COUNT
    # 4. add_message() - INSERT
    # 5. get_gender_preference() - SELECT
    # 6. get_user_messages() - SELECT
    # 7. add_message() - INSERT
```

### После FSM (2-3 запроса к БД)
```python
async def handle_message(message, user_service, ..., cached_user=None):
    # 1. add_user() - INSERT/UPDATE (обновляет кеш)
    # 2. can_send_message() - SELECT COUNT (не кешируется)
    # 3. add_message() - INSERT (не кешируется)
    # 4. add_message() - INSERT (не кешируется)
    
    # Кешированные данные:
    if cached_user:
        consent_given = cached_user.consent_given      # Из кеша
        gender = cached_user.gender_preference          # Из кеша
```

## Производительность

### Ожидаемые улучшения
- **Сокращение запросов к БД**: с 7+ до 2-3 на сообщение
- **Ускорение ответов**: на 50-80% для повторных запросов
- **Снижение нагрузки на БД**: особенно при высокой активности

### Мониторинг
```python
# Получение статистики кеша
stats = user_cache.get_stats()
print(f"Cache entries: {stats['total_entries']}")
print(f"Hit rate: {hit_rate}%")
```

## Управление кешем

### Инвалидация кеша
```python
# При изменении данных пользователя
await user_cache.invalidate(user_id)

# Или обновление конкретного поля
await user_cache.update_field(user_id, "consent_given", True)
```

### Очистка кеша
```python
# Полная очистка
await user_cache.clear()

# Автоматическая очистка устаревших данных
await user_cache._cleanup_expired()
```

## Лучшие практики

### 1. Порядок middleware
FSMMiddleware должен быть **раньше** AccessMiddleware, чтобы кеш был доступен для всех handlers.

### 2. Обработка cache miss
Всегда предусматривайте fallback на прямые запросы к БД:
```python
if cached_user:
    data = cached_user.field
else:
    data = await service.get_field(user_id)
```

### 3. Обновление кеша
При изменении данных пользователя обязательно обновляйте кеш:
```python
await service.update_field(user_id, new_value)
# Кеш автоматически обновится в CachedUserService
```

### 4. Мониторинг
Регулярно проверяйте:
- Hit rate кеша
- Размер кеша
- Время отклика handlers

## Troubleshooting

### Проблема: Кеш не работает
**Решение**: Проверьте порядок middleware и наличие FSMMiddleware в списке.

### Проблема: Устаревшие данные
**Решение**: Уменьшите TTL или добавьте инвалидацию кеша при критических изменениях.

### Проблема: Высокое потребление памяти
**Решение**: Уменьшите max_size или увеличьте частоту очистки.

## Будущие улучшения

1. **Redis интеграция** - для распределенного кеширования
2. **Cache warming** - предзагрузка популярных данных
3. **Metrics** - детальная статистика производительности
4. **Adaptive TTL** - динамическое изменение времени жизни кеша
