# Анализ масштабируемости системы мониторинга /metrics

## 🔍 Текущее состояние системы мониторинга

### Запросы к БД при каждом сообщении:

#### 1. **Обработка сообщения пользователя:**
```python
# В handle_message() - КАЖДОЕ сообщение
await user_service.add_user(user_id, username, first_name, last_name)  # 1-2 запроса
await user_service.get_consent_status(user_id)  # 1 запрос (если нет в кэше)
await message_service.can_send_message(user_id)  # 1 запрос к user_daily_counters
await message_service.add_message(user_id, "user", text)  # 1 запрос INSERT
await message_service.generate_response(user_id, text)  # 1 запрос SELECT для истории
await message_service.add_message(user_id, "assistant", response)  # 1 запрос INSERT
```

**Итого: 6-7 запросов к БД на каждое сообщение**

#### 2. **Метрики в памяти (без запросов к БД):**
```python
# Каждое сообщение - только обновления в памяти
safe_record_metric('record_message_processed')  # +1 в памяти
safe_record_user_interaction(user_id, "message")  # +1 в памяти + обновление set
safe_record_metric('record_cache_hit')  # +1 в памяти
safe_record_metric('record_successful_response', response_time)  # +1 в памяти
```

#### 3. **Сохранение метрик в БД:**
```python
# Каждые 5 минут (300 секунд) - 1 транзакция
await metrics_collector.save_to_database()  # 1 транзакция UPDATE/INSERT для всех метрик
```

## ⚠️ Проблемы масштабируемости

### При 1000 активных пользователей в день:
- **Сообщений в день:** ~10,000-50,000
- **Запросов к БД в день:** 60,000-350,000 (6-7 запросов на сообщение)
- **Сохранений метрик:** 288 раз в день (каждые 5 минут)

### При 10,000 активных пользователей в день:
- **Сообщений в день:** ~100,000-500,000
- **Запросов к БД в день:** 600,000-3,500,000
- **Сохранений метрик:** 288 раз в день (без изменений)

## 🚀 Оптимизации для масштабируемости

### 1. **Оптимизация запросов к БД на сообщение**

#### A. Batch операции для метрик:
```python
class MetricsCollector:
    def __init__(self):
        self._pending_metrics = {}  # Накапливаем изменения
        self._batch_size = 100      # Сохраняем каждые 100 изменений
        
    def record_message_processed(self):
        self._pending_metrics['total_messages_processed'] = \
            self._pending_metrics.get('total_messages_processed', 0) + 1
        
        # Сохраняем батчем
        if sum(self._pending_metrics.values()) >= self._batch_size:
            await self._flush_metrics_batch()
```

#### B. Уменьшение частоты сохранения:
```python
# Вместо каждых 5 минут - каждые 15-30 минут
await metrics_collector.start_auto_save(interval_seconds=900)  # 15 минут
```

### 2. **Оптимизация структуры БД для метрик**

#### A. Отдельная таблица для метрик в реальном времени:
```sql
CREATE TABLE real_time_metrics (
    metric_name TEXT PRIMARY KEY,
    metric_value BIGINT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индекс для быстрого обновления
CREATE INDEX idx_real_time_metrics_name ON real_time_metrics(metric_name);
```

#### B. Партиционирование по времени:
```sql
-- Партиции для исторических метрик
CREATE TABLE metrics_history (
    id SERIAL,
    metric_name TEXT NOT NULL,
    metric_value BIGINT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (recorded_at);
```

### 3. **Кэширование метрик**

#### A. Redis для метрик:
```python
import redis.asyncio as redis

class RedisMetricsCache:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
    
    async def increment_metric(self, metric_name: str, value: int = 1):
        await self.redis.incrby(f"metrics:{metric_name}", value)
    
    async def get_metrics_batch(self) -> Dict[str, int]:
        keys = await self.redis.keys("metrics:*")
        values = await self.redis.mget(keys)
        return {k.decode(): int(v) for k, v in zip(keys, values)}
```

### 4. **Асинхронное сохранение метрик**

#### A. Очередь для метрик:
```python
import asyncio
from asyncio import Queue

class AsyncMetricsQueue:
    def __init__(self):
        self.queue = Queue(maxsize=1000)
        self.worker_task = None
    
    async def start(self):
        self.worker_task = asyncio.create_task(self._worker())
    
    async def _worker(self):
        batch = []
        while True:
            try:
                metric = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                batch.append(metric)
                
                if len(batch) >= 50:  # Батч из 50 метрик
                    await self._save_batch(batch)
                    batch = []
            except asyncio.TimeoutError:
                if batch:
                    await self._save_batch(batch)
                    batch = []
```

### 5. **Оптимизация команды /metrics**

#### A. Кэширование результата:
```python
class MetricsCache:
    def __init__(self):
        self._cached_summary = None
        self._cache_ttl = 30  # секунд
        self._last_update = 0
    
    async def get_metrics_summary(self):
        now = time.time()
        if self._cached_summary and (now - self._last_update) < self._cache_ttl:
            return self._cached_summary
        
        # Обновляем кэш
        self._cached_summary = await self._build_summary()
        self._last_update = now
        return self._cached_summary
```

## 📊 Рекомендуемая архитектура для высоких нагрузок

### 1. **Трехуровневая система метрик:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   In-Memory     │ -> │   Redis Cache   │ -> │   PostgreSQL    │
│   (immediate)   │    │   (batch sync)  │    │   (persistent)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2. **Потоки данных:**
```
User Message -> In-Memory Metrics -> Redis (каждые 10 сек) -> PostgreSQL (каждые 5 мин)
```

### 3. **Команда /metrics:**
```
/metrics -> Redis Cache (TTL: 30 сек) -> Format & Return
```

## 🎯 Приоритетные оптимизации

### Высокий приоритет:
1. **Увеличить интервал автосохранения** с 5 до 15 минут
2. **Добавить кэширование команды /metrics** (TTL: 30 секунд)
3. **Batch операции для метрик** (накопление в памяти)

### Средний приоритет:
1. **Redis для метрик** (отдельный сервис)
2. **Асинхронная очередь метрик**
3. **Оптимизация структуры БД**

### Низкий приоритет:
1. **Партиционирование исторических данных**
2. **Мониторинг производительности метрик**
3. **Алерты по метрикам**

## 💡 Ожидаемый эффект

### После оптимизаций:
- **Запросы к БД для метрик:** с 288/день до 96/день (3x улучшение)
- **Время ответа /metrics:** с ~100ms до ~10ms (10x улучшение)
- **Нагрузка на БД:** снижение на 60-70%
- **Масштабируемость:** до 50,000+ пользователей в день
