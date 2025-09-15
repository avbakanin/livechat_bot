# Исправление ключей переводов

## Проблема
После подтверждения смены пола компаньона отображался текст `[gender.change_confirm]` вместо переведенного сообщения.

## Причина
Несоответствие ключей переводов в коде и файлах локализации:

1. **В коде использовался**: `gender.change_confirm`
2. **В переводах был**: `gender.change_confirmed`

3. **В коде использовался**: `gender.change_cancel`  
4. **В переводах был**: `gender.change_cancelled`

## Решение

### Исправлены ключи переводов:

**1. В `app/domain/user/handlers.py` строка 101:**
```python
# ❌ БЫЛО:
await callback.message.edit_text(i18n.t("gender.change_confirm"), ...)

# ✅ СТАЛО:
await callback.message.edit_text(i18n.t("gender.change_confirmed"), ...)
```

**2. В `app/domain/user/handlers.py` строка 112:**
```python
# ❌ БЫЛО:
await callback.message.edit_text(i18n.t("gender.change_cancel"))

# ✅ СТАЛО:
await callback.message.edit_text(i18n.t("gender.change_cancelled"))
```

## Результат

### Для русскоязычных пользователей:
После подтверждения смены пола теперь отображается:
- **Текст**: "История переписки удалена. Выбери пол компаньона:"
- **Кнопки**: "Выбрать девушку 😊" / "Выбрать молодого человека 😉"

### Для англоязычных пользователей:
- **Текст**: "Chat history deleted. Choose companion's gender:"
- **Кнопки**: "Choose girl 😊" / "Choose young man 😉"

## Проверенные ключи переводов

Все используемые ключи теперь соответствуют файлам переводов:
- ✅ `gender.change_warning` - предупреждение о смене пола
- ✅ `gender.change_confirmed` - подтверждение удаления истории
- ✅ `gender.change_cancelled` - отмена смены пола
- ✅ `gender.choose` - выбор пола
- ✅ `gender.toggle_gender` - уведомление об изменении пола
- ✅ `buttons.yes_change` / `buttons.cancel` - кнопки подтверждения

Теперь все переводы работают корректно! 🎉
