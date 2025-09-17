# Улучшения производительности - Кэширование безопасности

## Проблема
В `app/domain/message/handlers.py` на каждом сообщении создаются новые объекты:
```python
security_validator = SecurityValidator()
text_sanitizer = TextSanitizer()
security_logger = SecurityLogger()
```

## Решение
Создать singleton или кэшировать эти объекты для улучшения производительности.

### Реализация
```python
# app/shared/security/singleton.py
class SecuritySingleton:
    _instance = None
    _security_validator = None
    _text_sanitizer = None
    _security_logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def validator(self):
        if self._security_validator is None:
            self._security_validator = SecurityValidator()
        return self._security_validator
    
    @property
    def sanitizer(self):
        if self._text_sanitizer is None:
            self._text_sanitizer = TextSanitizer()
        return self._text_sanitizer
    
    @property
    def logger(self):
        if self._security_logger is None:
            self._security_logger = SecurityLogger()
        return self._security_logger

# Использование
security = SecuritySingleton()
security.validator.validate_user_behavior(user_id, "message")
```
