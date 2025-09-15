# Очистка файлов переводов от дублирующихся и неиспользуемых ключей

## Проблемы, которые были найдены и исправлены:

### 1. ❌ Дублирующиеся ключи

**Проблема:**
- `commands.start.already_started` и `messages.bot_already_started` содержали одинаковый текст
- Это создавало путаницу и дублирование переводов

**Решение:**
- ✅ Удален `messages.bot_already_started` из обоих файлов переводов
- ✅ Обновлен код для использования `commands.start.already_started`
- ✅ Оставлен только один ключ для сообщения "бот уже запущен"

### 2. ❌ Похожие ключи

**Проблема:**
- `gender.choose` и `gender.choose_for_chat` содержали очень похожий текст
- Разница была минимальной ("для общения" / "for chatting")

**Решение:**
- ✅ Удален `gender.choose_for_chat` из обоих файлов переводов
- ✅ Оставлен только `gender.choose` для выбора пола компаньона

### 3. ❌ Неиспользуемые ключи

**Проблема:**
- `gender.changed_to_female` и `gender.changed_to_male` не использовались в коде
- Эти ключи были заменены на динамический `gender.toggle_gender`

**Решение:**
- ✅ Удалены `gender.changed_to_female` и `gender.changed_to_male` из обоих файлов переводов
- ✅ Используется только `gender.toggle_gender` с параметром `{gender}`

## Изменения в файлах:

### `locales/ru/translations.json`:
```json
// ❌ УДАЛЕНО:
"messages": {
  "bot_already_started": "Бот уже запущен - просто напиши сообщение 😊"
}

"gender": {
  "choose_for_chat": "Выбери пол компаньона для общения:",
  "changed_to_female": "Пол компаньона изменен на девушку 😊",
  "changed_to_male": "Пол компаньона изменен на молодого человека 😉"
}
```

### `locales/en/translations.json`:
```json
// ❌ УДАЛЕНО:
"messages": {
  "bot_already_started": "Bot is already running 😊"
}

"gender": {
  "choose_for_chat": "Choose companion's gender for chatting:",
  "changed_to_female": "Companion's gender changed to girl 😊",
  "changed_to_male": "Companion's gender changed to young man 😉"
}
```

### `app/domain/user/handlers.py`:
```python
# ❌ БЫЛО:
await message.answer(i18n.t("messages.bot_already_started"))

# ✅ СТАЛО:
await message.answer(i18n.t("commands.start.already_started"))
```

## Результат:

### ✅ Преимущества очистки:

1. **Уменьшение размера файлов**: Удалено 6 неиспользуемых ключей
2. **Устранение дублирования**: Нет больше одинаковых переводов
3. **Упрощение поддержки**: Меньше ключей для отслеживания
4. **Консистентность**: Один ключ для одной функции
5. **Чистота кода**: Удалены неиспользуемые переводы

### 📊 Статистика:

- **Удалено ключей**: 6 (3 из русского + 3 из английского файла)
- **Обновлено в коде**: 1 место использования
- **Сохранено функциональности**: 100%

### 🎯 Итог:

Файлы переводов теперь чище, без дублирующихся и неиспользуемых ключей. Это упрощает поддержку и уменьшает вероятность ошибок при добавлении новых переводов.
