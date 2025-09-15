# 🔒 Система безопасности бота

## Обзор

Реализована комплексная система безопасности для Telegram-бота, включающая:

- **Санитизацию текста** - очистка от потенциально опасного контента
- **Валидацию поведения** - проверка на флуд и подозрительную активность  
- **Расширенное логирование** - детальное отслеживание событий безопасности
- **Метрики безопасности** - статистика угроз и инцидентов

## Компоненты

### 1. TextSanitizer (`app/shared/security/sanitizer.py`)

Очищает пользовательский ввод от:
- HTML/JavaScript инъекций
- SQL инъекций (дополнительная защита)
- Подозрительных символов и паттернов
- Контрольных символов

```python
from shared.security import TextSanitizer

sanitizer = TextSanitizer()
clean_text = sanitizer.sanitize_text(user_input, user_id)
```

### 2. SecurityValidator (`app/shared/security/validator.py`)

Проверяет:
- Длину сообщений
- Повторяющийся контент
- Подозрительные паттерны
- Поведение пользователя (флуд)

```python
from shared.security import SecurityValidator

validator = SecurityValidator()
result = validator.validate_message_content(text, user_id, 2500)
```

### 3. SecurityLogger (`app/shared/security/logger.py`)

Логирует события безопасности в структурированном формате:
- Подозрительный контент
- Попытки флуда
- Длинные сообщения
- Множественные флаги безопасности

## Интеграция

### Обработчик сообщений

```python
# Валидация поведения
behavior_validation = security_validator.validate_user_behavior(user_id, "message")
if not behavior_validation["is_valid"]:
    # Блокировка флуда
    return

# Валидация контента
content_validation = security_validator.validate_message_content(text, user_id, 2500)

# Санитизация
sanitized_text = text_sanitizer.sanitize_text(text, user_id)
```

### Метрики безопасности

Добавлены новые метрики:
- `security_flags` - количество флагов безопасности
- `suspicious_content_detected` - обнаруженный подозрительный контент
- `flood_attempts_blocked` - заблокированные попытки флуда
- `sanitization_applied` - примененная санитизация
- `access_denied_count` - отказы в доступе

### Команды

- `/security` - просмотр персональных метрик безопасности
- `/metrics` - общие метрики включая безопасность

## Логирование

События безопасности записываются в `security.log`:

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "event_type": "SUSPICIOUS_CONTENT",
  "user_id": 123456,
  "severity": "MEDIUM",
  "description": "Suspicious content detected",
  "details": {
    "patterns_found": ["<script>", "javascript:"],
    "original_length": 100,
    "sanitized_length": 80
  }
}
```

## Уровни серьезности

- **LOW** - Информационные события
- **MEDIUM** - Подозрительная активность
- **HIGH** - Потенциальные угрозы
- **CRITICAL** - Критические инциденты

## Безопасность по дизайну

1. **Параметризованные запросы** - защита от SQL-инъекций
2. **Валидация на всех уровнях** - входные данные, поведение, контент
3. **Санитизация** - очистка потенциально опасного контента
4. **Rate limiting** - защита от флуда
5. **Access control** - ограничение доступа по whitelist
6. **Структурированное логирование** - детальное отслеживание

## Мониторинг

Система автоматически отслеживает:
- Подозрительные паттерны в сообщениях
- Быстрые последовательности сообщений
- Повторяющийся контент
- Попытки доступа неавторизованных пользователей
- Применение санитизации

Все события логируются с соответствующими метриками для анализа безопасности.
