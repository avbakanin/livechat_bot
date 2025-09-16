# 📊 **ДОКУМЕНТАЦИЯ ПО МЕТРИКАМ И МОНИТОРИНГУ**

## 📋 **ОБЗОР СИСТЕМЫ МЕТРИК**

LiveChat Bot использует **продвинутую систему метрик** с категоризацией, временными окнами и автоматическими алертами для комплексного мониторинга производительности, безопасности и бизнес-показателей.

### 🎯 **Принципы метрик**

1. **Категоризация** - метрики разделены по типам и назначению
2. **Временные окна** - поддержка различных временных интервалов
3. **Автоматические алерты** - уведомления о критических событиях
4. **Экспорт** - интеграция с внешними системами мониторинга
5. **Визуализация** - дашборды для анализа данных

---

## 🏗️ **АРХИТЕКТУРА СИСТЕМЫ МЕТРИК**

### **Компоненты системы:**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│ Metrics Collector│───▶│   Dashboard     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Alert System  │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Export System   │
                       └─────────────────┘
```

---

## 📊 **КАТЕГОРИИ МЕТРИК**

### **1. System Metrics** 🖥️
**Назначение**: Мониторинг системных ресурсов

| Метрика | Тип | Описание | Логика |
|---------|-----|----------|--------|
| `system_uptime_seconds` | GAUGE | Время работы системы | Время с момента запуска |
| `system_memory_usage_mb` | GAUGE | Использование памяти | Текущее потребление RAM |
| `system_cpu_usage_percent` | GAUGE | Использование CPU | Процент загрузки процессора |

**Пример использования:**
```python
from shared.metrics.advanced_metrics import metrics_manager

# Запись метрики использования памяти
metrics_manager.system.record_memory_usage(512.5)  # 512.5 MB

# Запись метрики CPU
metrics_manager.system.record_cpu_usage(75.2)  # 75.2%
```

### **2. Performance Metrics** ⚡
**Назначение**: Мониторинг производительности

| Метрика | Тип | Описание | Логика |
|---------|-----|----------|--------|
| `response_time_message_ms` | TIMER | Время ответа на сообщение | Среднее время обработки |
| `response_time_command_ms` | TIMER | Время выполнения команды | Время обработки команд |
| `database_query_time_ms` | TIMER | Время запросов к БД | Производительность БД |
| `cache_hit` | COUNTER | Попадания в кэш | Эффективность кэширования |

**Пример использования:**
```python
# Запись времени ответа
metrics_manager.performance.record_response_time("message", 150.5)  # 150.5ms

# Запись производительности кэша
metrics_manager.performance.record_cache_performance("user_cache", hit=True)
```

### **3. Business Metrics** 💰
**Назначение**: Бизнес-показатели и KPI

| Метрика | Тип | Описание | Логика |
|---------|-----|----------|--------|
| `user_registration` | COUNTER | Регистрации пользователей | Счетчик новых пользователей |
| `subscription_change` | COUNTER | Изменения подписок | Переходы между планами |
| `revenue` | COUNTER | Доходы | Накопленная выручка |
| `user_engagement_score` | GAUGE | Вовлеченность пользователей | Оценка активности |

**Пример использования:**
```python
# Запись регистрации пользователя
metrics_manager.business.record_user_registration(12345, source="telegram")

# Запись изменения подписки
metrics_manager.business.record_subscription_change(12345, "free", "premium")

# Запись дохода
metrics_manager.business.record_revenue(299.0, currency="RUB", source="subscription")
```

### **4. User Metrics** 👥
**Назначение**: Поведение и активность пользователей

| Метрика | Тип | Описание | Логика |
|---------|-----|----------|--------|
| `user_activity` | COUNTER | Активность пользователей | Счетчик взаимодействий |
| `session_duration_minutes` | TIMER | Длительность сессий | Время активности |
| `user_satisfaction_score` | GAUGE | Удовлетворенность | Оценка пользователей |

**Пример использования:**
```python
# Запись активности пользователя
metrics_manager.user.record_user_activity(12345, "message_sent")

# Запись длительности сессии
metrics_manager.user.record_session_duration(12345, 15.5)  # 15.5 минут

# Запись оценки удовлетворенности
metrics_manager.user.record_user_satisfaction(12345, 4)  # 4 из 5
```

### **5. Security Metrics** 🔒
**Назначение**: Мониторинг безопасности

| Метрика | Тип | Описание | Логика |
|---------|-----|----------|--------|
| `security_event` | COUNTER | События безопасности | Счетчик инцидентов |
| `attack_blocked` | COUNTER | Заблокированные атаки | Предотвращенные угрозы |
| `user_blocked` | COUNTER | Заблокированные пользователи | Блокировки по нарушениям |

**Пример использования:**
```python
# Запись события безопасности
metrics_manager.security.record_security_event("sql_injection", "high", user_id=12345)

# Запись заблокированной атаки
metrics_manager.security.record_attack_blocked("xss", user_id=12345)

# Запись блокировки пользователя
metrics_manager.security.record_user_blocked(12345, "spam", 24)  # 24 часа
```

### **6. Quality Metrics** 📈
**Назначение**: Качество ответов и сервиса

| Метрика | Тип | Описание | Логика |
|---------|-----|----------|--------|
| `response_quality_score` | GAUGE | Качество ответов | Оценка качества AI |
| `user_feedback` | GAUGE | Отзывы пользователей | Обратная связь |

**Пример использования:**
```python
# Запись качества ответа
metrics_manager.quality.record_response_quality("resp_123", 4.2)  # 4.2 из 5

# Запись отзыва пользователя
metrics_manager.quality.record_user_feedback(12345, "rating", 5)  # 5 звезд
```

### **7. Error Metrics** ❌
**Назначение**: Мониторинг ошибок

| Метрика | Тип | Описание | Логика |
|---------|-----|----------|--------|
| `error_occurred` | COUNTER | Возникшие ошибки | Счетчик ошибок |
| `error_rate_percent` | GAUGE | Процент ошибок | Частота ошибок |

**Пример использования:**
```python
# Запись ошибки
metrics_manager.error.record_error("database", "connection_timeout", "db_service")

# Запись процента ошибок
metrics_manager.error.record_error_rate("api", 2.5)  # 2.5%
```

---

## ⏰ **ВРЕМЕННЫЕ ОКНА**

### **Поддерживаемые интервалы:**

| Окно | Описание | Использование |
|------|----------|---------------|
| `MINUTE` | Минутные метрики | Real-time мониторинг |
| `HOUR` | Часовые метрики | Краткосрочный анализ |
| `DAY` | Дневные метрики | Ежедневная отчетность |
| `WEEK` | Недельные метрики | Трендовый анализ |
| `MONTH` | Месячные метрики | Долгосрочная аналитика |

**Пример использования:**
```python
from shared.metrics.advanced_metrics import TimeWindow

# Запись метрики с часовым окном
metrics_manager.collector.record_metric(
    name="hourly_requests",
    value=150,
    category=MetricCategory.PERFORMANCE,
    time_window=TimeWindow.HOUR
)
```

---

## 🚨 **СИСТЕМА АЛЕРТОВ**

### **Уровни серьезности:**

| Уровень | Описание | Действия |
|---------|----------|----------|
| `LOW` | Низкий приоритет | Логирование |
| `MEDIUM` | Средний приоритет | Уведомление администратора |
| `HIGH` | Высокий приоритет | Автоматические действия |
| `CRITICAL` | Критический | Немедленное вмешательство |

### **Предустановленные правила:**

```python
from shared.metrics.alerts import AlertRule, AlertSeverity

# Высокое время ответа
AlertRule(
    name="high_response_time",
    metric_name="response_time_message_ms",
    condition=">",
    threshold=5000.0,  # 5 секунд
    severity=AlertSeverity.HIGH,
    description="Response time is too high"
)

# Низкий процент попаданий в кэш
AlertRule(
    name="low_cache_hit_rate",
    metric_name="cache_hit_rate_percent",
    condition="<",
    threshold=70.0,  # 70%
    severity=AlertSeverity.MEDIUM,
    description="Cache hit rate is too low"
)

# Высокий процент ошибок
AlertRule(
    name="high_error_rate",
    metric_name="error_rate_percent",
    condition=">",
    threshold=5.0,  # 5%
    severity=AlertSeverity.CRITICAL,
    description="Error rate is too high"
)
```

### **Каналы уведомлений:**

```python
from shared.metrics.alerts import alert_manager, NotificationChannels

# Добавление каналов уведомлений
alert_manager.add_notification_channel(NotificationChannels.console_notification)
alert_manager.add_notification_channel(NotificationChannels.log_notification)
alert_manager.add_notification_channel(NotificationChannels.file_notification)

# Webhook уведомления
alert_manager.add_notification_channel(
    lambda alert: NotificationChannels.webhook_notification(alert, "https://hooks.slack.com/...")
)
```

---

## 📊 **ДАШБОРДЫ**

### **HTML Dashboard:**
```python
from shared.metrics.dashboard import metrics_dashboard

# Генерация HTML дашборда
html_dashboard = metrics_dashboard.generate_html_dashboard(hours=24)

# Сохранение в файл
with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_dashboard)
```

### **JSON API:**
```python
# Генерация JSON API
json_data = metrics_dashboard.generate_json_api(hours=24)
```

### **Prometheus метрики:**
```python
# Генерация Prometheus формата
prometheus_metrics = metrics_dashboard.generate_prometheus_metrics()
```

---

## 📤 **ЭКСПОРТ МЕТРИК**

### **Поддерживаемые форматы:**

| Формат | Описание | Использование |
|--------|----------|---------------|
| `JSON` | Стандартный JSON | API интеграции |
| `CSV` | Табличный формат | Excel анализ |
| `XML` | XML формат | Корпоративные системы |
| `Prometheus` | Prometheus формат | Мониторинг |
| `InfluxDB` | InfluxDB формат | Временные ряды |
| `Grafana` | Grafana JSON | Визуализация |
| `Datadog` | Datadog формат | APM |
| `New Relic` | New Relic формат | APM |
| `Splunk` | Splunk формат | Логирование |
| `Elasticsearch` | Elasticsearch формат | Поиск |

### **Примеры экспорта:**

```python
from shared.metrics.export import metrics_exporter

# Экспорт в JSON
json_data = metrics_exporter.export("json", hours=24, filename="metrics.json")

# Экспорт в CSV
csv_data = metrics_exporter.export("csv", hours=24, filename="metrics.csv")

# Экспорт в Prometheus
prometheus_data = metrics_exporter.export("prometheus", hours=1)

# Экспорт в Grafana
grafana_data = metrics_exporter.export("grafana", hours=24)

# Кастомный формат
custom_data = metrics_exporter.export(
    "custom", 
    hours=24,
    format_template="Metric: {category}.{metric} = {value} (avg: {avg})"
)
```

---

## 🔧 **ИНТЕГРАЦИЯ С СУЩЕСТВУЮЩЕЙ СИСТЕМОЙ**

### **Обновление обработчиков:**

```python
# app/domain/message/handlers.py
from shared.metrics.advanced_metrics import metrics_manager
from shared.metrics.alerts import alert_manager

async def handle_message(message: Message, ...):
    start_time = time.time()
    
    try:
        # Обработка сообщения
        response = await process_message(message.text)
        
        # Запись метрик
        response_time = (time.time() - start_time) * 1000
        metrics_manager.performance.record_response_time("message", response_time)
        metrics_manager.user.record_user_activity(message.from_user.id, "message_sent")
        
        # Проверка алертов
        summary = metrics_manager.get_comprehensive_summary(1)
        await alert_manager.check_metrics(summary)
        
    except Exception as e:
        # Запись ошибки
        metrics_manager.error.record_error("message_processing", str(e), "message_handler")
        raise
```

### **Middleware для автоматических метрик:**

```python
# app/core/middleware.py
from shared.metrics.advanced_metrics import metrics_manager

class MetricsMiddleware:
    def __init__(self):
        self.name = "metrics"
        
    async def __call__(self, handler, event, data):
        start_time = time.time()
        
        try:
            result = await handler(event, data)
            
            # Запись успешного выполнения
            response_time = (time.time() - start_time) * 1000
            metrics_manager.performance.record_response_time("handler", response_time)
            
            return result
            
        except Exception as e:
            # Запись ошибки
            metrics_manager.error.record_error("handler", str(e), "middleware")
            raise
```

---

## 📈 **АНАЛИЗ И ОПТИМИЗАЦИЯ**

### **Ключевые показатели эффективности (KPI):**

| KPI | Описание | Целевое значение |
|-----|----------|------------------|
| **Response Time** | Время ответа | < 2 секунды |
| **Error Rate** | Процент ошибок | < 1% |
| **Cache Hit Rate** | Попадания в кэш | > 80% |
| **User Satisfaction** | Удовлетворенность | > 4.0/5 |
| **Uptime** | Время работы | > 99.9% |
| **Security Score** | Балл безопасности | > 90/100 |

### **Метрики для мониторинга:**

```python
# Получение сводки метрик
summary = metrics_manager.get_comprehensive_summary(hours=24)

# Анализ производительности
response_time = summary['performance']['response_time_message_ms']['avg']
if response_time > 2000:  # 2 секунды
    print("⚠️ High response time detected")

# Анализ ошибок
error_rate = summary['error']['error_rate_percent']['latest']
if error_rate > 1.0:  # 1%
    print("🚨 High error rate detected")

# Анализ безопасности
security_events = summary['security']['security_event']['sum']
if security_events > 10:
    print("🔒 Multiple security events detected")
```

---

## 🚀 **ПРОИЗВОДИТЕЛЬНОСТЬ И МАСШТАБИРОВАНИЕ**

### **Оптимизация:**

1. **Батчевое сохранение** - группировка метрик для записи
2. **Асинхронная обработка** - неблокирующие операции
3. **Кэширование** - хранение часто используемых метрик
4. **Сжатие данных** - оптимизация хранения
5. **Партиционирование** - разделение по времени

### **Мониторинг производительности:**

```python
# Мониторинг самой системы метрик
metrics_manager.system.record_memory_usage(get_memory_usage())
metrics_manager.system.record_cpu_usage(get_cpu_usage())

# Проверка производительности записи метрик
start_time = time.time()
for i in range(1000):
    metrics_manager.performance.record_response_time("test", 100.0)
write_time = (time.time() - start_time) * 1000

print(f"1000 metrics written in {write_time:.2f}ms")
```

---

## ✅ **ЗАКЛЮЧЕНИЕ**

Система метрик LiveChat Bot обеспечивает:

- **📊 Комплексный мониторинг** - все аспекты системы
- **🚨 Автоматические алерты** - раннее обнаружение проблем
- **📈 Визуализация** - понятные дашборды
- **📤 Экспорт** - интеграция с внешними системами
- **⚡ Производительность** - оптимизированная работа
- **🔧 Гибкость** - настраиваемые правила и форматы

**Система готова для production использования и обеспечивает полную видимость работы бота!** 🚀
