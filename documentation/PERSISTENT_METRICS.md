# 💾 Персистентные метрики бота

## 📋 **Проблема**

Ранее данные для команды `/metrics` **обнулялись при перезапуске** `main.py` из-за хранения метрик только в памяти.

## 🔧 **Решение**

Реализована **персистентная система метрик** с сохранением в PostgreSQL и автоматическим восстановлением после перезапуска.

## 🏗️ **Архитектура**

### **1. База данных**

#### **Таблица `bot_metrics`:**
```sql
CREATE TABLE public.bot_metrics (
    id SERIAL PRIMARY KEY,
    metric_name TEXT NOT NULL UNIQUE,
    metric_value BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **Функции БД:**
```sql
-- Получить значение метрики
public.get_metric(metric_name TEXT) RETURNS BIGINT

-- Установить значение метрики
public.set_metric(metric_name TEXT, value BIGINT) RETURNS VOID

-- Увеличить значение метрики
public.increment_metric(metric_name TEXT, increment BIGINT DEFAULT 1) RETURNS VOID
```

### **2. Сервис метрик**

#### **`MetricsService` (`app/services/metrics/metrics_service.py`):**
```python
class MetricsService:
    async def get_metric(self, metric_name: str) -> int
    async def set_metric(self, metric_name: str, value: int) -> None
    async def increment_metric(self, metric_name: str, increment: int = 1) -> None
    async def get_all_metrics(self) -> Dict[str, int]
    async def save_metrics(self, metrics: Dict[str, Any]) -> None
    async def load_metrics(self) -> Dict[str, int]
```

### **3. Обновленный MetricsCollector**

#### **Новые методы:**
```python
class MetricsCollector:
    async def load_from_database(self):
        """Загрузить метрики из БД при запуске"""
    
    async def save_to_database(self):
        """Сохранить текущие метрики в БД"""
    
    async def start_auto_save(self, interval_seconds: int = 300):
        """Автоматическое сохранение каждые 5 минут"""
    
    async def stop_auto_save(self):
        """Остановить автоматическое сохранение"""
```

## 🔄 **Жизненный цикл метрик**

### **При запуске бота:**
```python
# 1. Создается MetricsService с подключением к БД
metrics_service = MetricsService(pool)

# 2. Инициализируется MetricsCollector с сервисом
metrics_collector.metrics_service = metrics_service

# 3. Загружаются метрики из БД
await metrics_collector.load_from_database()

# 4. Запускается автосохранение каждые 5 минут
await metrics_collector.start_auto_save(interval_seconds=300)
```

### **Во время работы:**
```python
# Метрики записываются в память как обычно
metrics_collector.record_message_processed()
metrics_collector.record_successful_response(response_time)

# Каждые 5 минут автоматически сохраняются в БД
# (выполняется в фоновом режиме)
```

### **При остановке бота:**
```python
# 1. Сохраняются текущие метрики в БД
await metrics_collector.save_to_database()

# 2. Останавливается автосохранение
await metrics_collector.stop_auto_save()
```

## 📊 **Сохраненные метрики**

### **Основные метрики:**
- `total_messages_processed` - общее количество сообщений
- `successful_responses` - успешные ответы
- `failed_responses` - неудачные ответы
- `limit_exceeded_count` - превышения лимитов
- `active_users_today` - активные пользователи сегодня
- `new_users_today` - новые пользователи сегодня

### **Метрики ошибок:**
- `openai_errors` - ошибки OpenAI API
- `database_errors` - ошибки базы данных
- `validation_errors` - ошибки валидации

### **Метрики кэша:**
- `cache_hits` - попадания в кэш
- `cache_misses` - промахи кэша

### **Метрики производительности:**
- `total_response_time` - общее время ответов
- `average_response_time` - среднее время ответов
- `uptime_seconds` - время работы в секундах

### **Временные метки:**
- `started_at` - время запуска бота (Unix timestamp)
- `last_reset` - время последнего сброса (Unix timestamp)

## 🔄 **Автоматическое сохранение**

### **Настройки:**
- **Интервал:** каждые 5 минут (300 секунд)
- **Фоновый режим:** не блокирует основную работу бота
- **Обработка ошибок:** логируются, но не прерывают работу

### **Логика:**
```python
async def _auto_save_loop():
    while self._auto_save_enabled:
        try:
            await asyncio.sleep(300)  # 5 минут
            if self._auto_save_enabled:
                await self.save_to_database()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logging.error(f"Error in auto-save loop: {e}")
```

## 🛡️ **Надежность**

### **1. Восстановление после сбоев:**
- Метрики сохраняются каждые 5 минут
- При перезапуске загружаются из БД
- Потеря данных минимальна (максимум 5 минут)

### **2. Обработка ошибок:**
- Ошибки БД логируются, но не прерывают работу
- При ошибке загрузки возвращаются пустые метрики
- Автосохранение продолжает работать при ошибках

### **3. Graceful shutdown:**
- При остановке бота метрики сохраняются принудительно
- Автосохранение корректно останавливается
- Нет потери данных при завершении

## 📈 **Преимущества**

### **1. Персистентность:**
- ✅ Метрики сохраняются между перезапусками
- ✅ Нет потери исторических данных
- ✅ Корректное время работы (uptime)

### **2. Производительность:**
- ✅ Минимальное влияние на основную работу
- ✅ Автосохранение в фоновом режиме
- ✅ Эффективные SQL функции

### **3. Надежность:**
- ✅ Автоматическое восстановление
- ✅ Обработка ошибок БД
- ✅ Graceful shutdown

## 🔍 **Мониторинг**

### **Логи:**
```
📊 Loaded metrics from database
📊 Started auto-save every 300 seconds
📊 Saved metrics to database
📊 Stopped auto-save
```

### **Проверка в БД:**
```sql
-- Просмотр всех метрик
SELECT metric_name, metric_value, updated_at 
FROM public.bot_metrics 
ORDER BY updated_at DESC;

-- Проверка времени последнего обновления
SELECT metric_name, metric_value, updated_at 
FROM public.bot_metrics 
WHERE metric_name = 'total_messages_processed';
```

## ✅ **Результат**

Теперь данные для команды `/metrics` **НЕ обнуляются** при перезапуске:

- ✅ **Персистентность** - метрики сохраняются в БД
- ✅ **Автовосстановление** - загрузка при запуске
- ✅ **Автосохранение** - каждые 5 минут
- ✅ **Graceful shutdown** - сохранение при остановке
- ✅ **Надежность** - обработка ошибок

**Время работы (uptime) теперь корректно отслеживается с момента первого запуска!**
