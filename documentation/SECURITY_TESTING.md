# Примеры тестирования системы безопасности

## Тестовые сценарии

### 1. SQL-инъекции
```
'; DROP TABLE users; --
UNION SELECT * FROM users
INSERT INTO users VALUES (1, 'hacker')
```

### 2. XSS атаки
```
<script>alert('XSS')</script>
<img src="x" onerror="alert('XSS')">
javascript:alert('XSS')
```

### 3. Флуд
- Отправка множества сообщений подряд
- Повторяющийся контент
- Очень длинные сообщения

### 4. Подозрительные символы
```
<iframe src="evil.com"></iframe>
<object data="malware.exe"></object>
data:text/html,<script>alert('XSS')</script>
```

## Ожидаемое поведение

1. **SQL-инъекции** - полностью блокируются параметризованными запросами
2. **XSS** - HTML теги удаляются, JavaScript блокируется
3. **Флуд** - ограничивается по времени между сообщениями
4. **Подозрительный контент** - логируется и санитизируется

## Команды для проверки

```bash
# Просмотр логов безопасности
tail -f security.log

# Поиск подозрительной активности
grep "SECURITY" security.log

# Статистика по типам угроз
grep "SUSPICIOUS_CONTENT" security.log | wc -l
grep "FLOOD_ATTEMPT" security.log | wc -l
```
