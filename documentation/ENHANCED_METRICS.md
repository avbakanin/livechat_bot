# 📊 Расширенные метрики бота

## 📋 **Описание**

Добавлены недостающие метрики для команды `/metrics`, включая запись новых пользователей, активных пользователей, времени ответов и метрик фоновых задач.

## 🔧 **Добавленные метрики**

### **1. Новые пользователи (`record_new_user`)**

#### **Где записывается:**
- **`app/domain/user/handlers.py`** - в функции `cmd_start()`

#### **Логика:**
```python
# Check if user is new before adding
user_exists = await user_service.get_user(user_id) is not None

await user_service.add_user(user_id, username, first_name, last_name)

# Record new user if this is their first time
if not user_exists:
    metrics_collector.record_new_user()
```

#### **Что отслеживает:**
- Количество новых пользователей, запустивших бота впервые
- Увеличивает счетчик `new_users_today`

### **2. Активные пользователи (`record_active_user`)**

#### **Где записывается:**
- **`app/domain/user/handlers.py`** - в функции `cmd_start()`
- **`app/domain/message/handlers.py`** - в функции `handle_message()`

#### **Логика:**
```python
# Always record as active user
metrics_collector.record_active_user()
```

#### **Что отслеживает:**
- Количество пользователей, взаимодействующих с ботом
- Увеличивает счетчик `active_users_today`

### **3. Время ответов (`record_successful_response`)**

#### **Где записывается:**
- **`app/domain/message/handlers.py`** - при генерации ответов ИИ

#### **Логика:**
```python
# Generate AI response with timing
start_time = time.time()
answer = await message_service.generate_response(user_id, message.text, gender)
response_time = time.time() - start_time

# Record successful response with timing
metrics_collector.record_successful_response(response_time)
```

#### **Что отслеживает:**
- Время генерации ответов ИИ
- Обновляет `average_response_time`
- Увеличивает счетчик `successful_responses`

### **4. Метрики фоновых задач**

#### **DailyResetTask:**
```python
# Record metrics for successful reset
metrics_collector.record_successful_response(0.0)  # Reset operation time

# Record error metrics
metrics_collector.record_failed_response("database")
```

#### **PartitionManagementTask:**
```python
# Record metrics for successful partition creation
metrics_collector.record_successful_response(0.0)

# Record error metrics
metrics_collector.record_failed_response("database")
```

#### **Что отслеживает:**
- Успешные операции сброса счетчиков и управления партициями
- Ошибки в фоновых задачах
- Время выполнения операций

## 📊 **Обновленные метрики в `/metrics`**

### **Теперь доступны:**

```python
{
    "uptime_seconds": время работы в секундах,
    "uptime_hours": время работы в часах,
    "total_messages": общее количество сообщений,
    "success_rate": процент успешных ответов,
    "cache_hit_rate": процент попаданий в кэш,
    "average_response_time": среднее время ответа ИИ,
    "active_users_today": активные пользователи сегодня,  # ← НОВОЕ
    "new_users_today": новые пользователи сегодня,        # ← НОВОЕ
    "limit_exceeded_count": количество превышений лимита,
    "openai_errors": ошибки OpenAI,
    "database_errors": ошибки базы данных,                # ← РАСШИРЕНО
    "validation_errors": ошибки валидации,
}
```

## 🔍 **Детализация метрик**

### **1. Пользователи:**
- **`new_users_today`** - пользователи, впервые запустившие `/start`
- **`active_users_today`** - пользователи, отправившие сообщения или команды

### **2. Производительность:**
- **`average_response_time`** - среднее время генерации ответов ИИ
- **`success_rate`** - процент успешных ответов (включая фоновые задачи)

### **3. Ошибки:**
- **`openai_errors`** - ошибки API OpenAI
- **`database_errors`** - ошибки БД (включая фоновые задачи)
- **`validation_errors`** - ошибки валидации сообщений

### **4. Кэш:**
- **`cache_hit_rate`** - процент попаданий в FSM кэш
- **`cache_hits`** - количество попаданий
- **`cache_misses`** - количество промахов

## 🚀 **Преимущества**

### **1. Полная картина:**
- Отслеживание всех аспектов работы бота
- Метрики пользователей, производительности и ошибок
- Мониторинг фоновых задач

### **2. Производительность:**
- Измерение времени ответов ИИ
- Отслеживание эффективности кэша
- Мониторинг ошибок по типам

### **3. Пользователи:**
- Количество новых пользователей
- Активность пользователей
- Превышения лимитов

### **4. Надежность:**
- Отслеживание ошибок в фоновых задачах
- Мониторинг операций с БД
- Контроль качества работы

## 📈 **Пример вывода `/metrics`**

```
📊 Bot Metrics

uptime_seconds: 86400
uptime_hours: 24.0
total_messages: 1250
success_rate: 98.5%
cache_hit_rate: 85.2%
average_response_time: 2.34s
active_users_today: 45
new_users_today: 12
limit_exceeded_count: 8
openai_errors: 15
database_errors: 3
validation_errors: 2
```

## ✅ **Результат**

Теперь команда `/metrics` предоставляет полную картину работы бота:
- ✅ **Пользователи** - новые и активные
- ✅ **Производительность** - время ответов ИИ
- ✅ **Ошибки** - детализация по типам
- ✅ **Фоновые задачи** - мониторинг операций
- ✅ **Кэш** - эффективность FSM кэширования

Все метрики записываются автоматически и доступны администраторам через команду `/metrics`.
