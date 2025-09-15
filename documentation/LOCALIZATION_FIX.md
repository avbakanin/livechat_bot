# Исправление локализации - все элементы интерфейса теперь на одном языке

## Проблема
В интерфейсе бота была смешанная локализация:
- **Текст предупреждения**: на русском языке (захардкожен)
- **Кнопки**: на английском языке (использовали i18n)

Это создавало непоследовательный пользовательский опыт.

## Причина
В файле `app/domain/user/messages.py` тексты были захардкожены на русском языке вместо использования системы i18n.

## Решение

### 1. Обновлен `app/domain/user/messages.py`
```python
# ❌ БЫЛО (захардкожено на русском):
def get_gender_change_warning_text() -> str:
    return "⚠️ Вы уверены, что хотите сменить пол компаньона?\n\nВся история переписки будет удалена!"

# ✅ СТАЛО (использует i18n):
def get_gender_change_warning_text() -> str:
    return i18n.t("gender.change_warning")
```

### 2. Обновлен `app/domain/user/keyboards.py`
Все функции keyboard теперь принимают параметр `i18n`:
```python
# ❌ БЫЛО:
def get_gender_change_confirmation_keyboard() -> InlineKeyboardMarkup:

# ✅ СТАЛО:
def get_gender_change_confirmation_keyboard(i18n: I18nMiddleware) -> InlineKeyboardMarkup:
```

### 3. Обновлены handlers
Все вызовы keyboard функций теперь передают параметр `i18n`:
```python
# ❌ БЫЛО:
await message.answer(get_gender_change_warning_text(), reply_markup=get_gender_change_confirmation_keyboard())

# ✅ СТАЛО:
await message.answer(i18n.t("gender.change_warning"), reply_markup=get_gender_change_confirmation_keyboard(i18n))
```

## Результат

### Для русскоязычных пользователей:
- **Текст**: "⚠️ Вы уверены, что хотите сменить пол компаньона? Вся история переписки будет удалена!"
- **Кнопки**: "Да, сменить пол" / "Отмена"

### Для англоязычных пользователей:
- **Текст**: "⚠️ Are you sure you want to change companion's gender? All chat history will be deleted!"
- **Кнопки**: "Yes, change gender" / "Cancel"

## Преимущества исправления

1. **✅ Консистентность**: Весь интерфейс на одном языке
2. **✅ Локализация**: Правильное определение языка пользователя
3. **✅ Масштабируемость**: Легко добавлять новые языки
4. **✅ Поддержка**: Централизованное управление переводами

## Файлы переводов

Переводы уже существуют в:
- `locales/ru/translations.json` - русские переводы
- `locales/en/translations.json` - английские переводы

Ключи переводов:
- `gender.change_warning` - текст предупреждения
- `buttons.yes_change` - кнопка "Да, сменить пол"
- `buttons.cancel` - кнопка "Отмена"

Теперь локализация работает корректно! 🎉
