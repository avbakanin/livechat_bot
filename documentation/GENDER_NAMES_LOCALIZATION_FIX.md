# Исправление локализации названий полов

## Проблема
В сообщениях о смене пола компаньона была смешанная локализация:
- **Статическая часть**: "Companion's gender changed to" (на английском)
- **Динамическая часть**: "молодого человека", "девушку" (захардкожено на русском)

## Причина
В функции `gender_choice` названия полов были захардкожены на русском языке:

```python
# ❌ ПРОБЛЕМА:
response_text = "девушку 😊" if preference == "female" else "молодого человека 😉"
await callback.message.edit_text(i18n.t("gender.toggle_gender", gender=response_text))
```

## Решение

### Исправлена функция `gender_choice`:

```python
# ✅ ИСПРАВЛЕНО:
# Use translated gender names
gender_name = i18n.t("buttons.female") if preference == "female" else i18n.t("buttons.male")
await callback.message.edit_text(i18n.t("gender.toggle_gender", gender=gender_name))
```

### Исправлены функции с отсутствующим параметром `i18n`:

**1. Функция `cmd_help`:**
```python
# ❌ БЫЛО:
async def cmd_help(message: Message, user_service: UserService):

# ✅ СТАЛО:
async def cmd_help(message: Message, user_service: UserService, i18n: I18nMiddleware):
```

**2. Функция `back_to_help`:**
```python
# ❌ БЫЛО:
async def back_to_help(callback: CallbackQuery):

# ✅ СТАЛО:
async def back_to_help(callback: CallbackQuery, i18n: I18nMiddleware):
```

## Результат

### Для русскоязычных пользователей:
- **Текст**: "Пол компаньона изменен на Девушка 😊 😊"
- **Или**: "Пол компаньона изменен на Молодой человек 😉 😉"

### Для англоязычных пользователей:
- **Текст**: "Companion's gender changed to Girl 😊 😊"
- **Или**: "Companion's gender changed to Young man 😉 😉"

## Используемые ключи переводов

- `gender.toggle_gender` - шаблон сообщения о смене пола
- `buttons.female` - название женского пола ("Девушка 😊" / "Girl 😊")
- `buttons.male` - название мужского пола ("Молодой человек 😉" / "Young man 😉")

## Преимущества исправления

1. **✅ Полная локализация**: Весь текст на одном языке
2. **✅ Консистентность**: Использование централизованных переводов
3. **✅ Масштабируемость**: Легко добавлять новые языки
4. **✅ Поддержка**: Все переводы в файлах локализации

Теперь все сообщения о смене пола полностью локализованы! 🎉
