# Интернационализация (i18n) для Telegram бота

Система интернационализации позволяет поддерживать несколько языков в боте. В настоящее время поддерживаются русский и английский языки.

## Структура файлов

```
app/shared/i18n/
├── __init__.py              # Основной класс I18nManager
└── translations.json         # JSON файл с переводами
```

## Использование

### 1. Автоматическое определение языка

Middleware `I18nMiddleware` автоматически определяет язык пользователя на основе его настроек Telegram и устанавливает соответствующий язык для всех сообщений.

```python
# В main.py уже подключен middleware
dp.message.middleware(I18nMiddleware())
dp.callback_query.middleware(I18nMiddleware())
```

### 2. Получение переводов в обработчиках

```python
@router.message()
async def handle_message(message: Message, i18n):
    # Получение перевода
    text = i18n.t("commands.start.welcome", free_limit=100)
    await message.answer(text)
```

### 3. Использование в функциях сообщений

```python
from shared.i18n import i18n

def get_help_text() -> str:
    return f"""
{hbold(i18n.t('commands.help.title'))}

{hbold(i18n.t('commands.help.commands_title'))}
{i18n.t('commands.help.start_command')}
"""
```

### 4. Использование в клавиатурах

```python
from shared.i18n import i18n

def get_gender_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=i18n.t("buttons.choose_female"), 
                callback_data="gender_female"
            ),
            InlineKeyboardButton(
                text=i18n.t("buttons.choose_male"), 
                callback_data="gender_male"
            )
        ]
    ])
```

## Структура переводов

Переводы организованы в иерархической структуре:

```json
{
  "ru": {
    "commands": {
      "start": {
        "welcome": "Привет! У тебя {free_limit} бесплатных сообщений в день."
      }
    },
    "buttons": {
      "choose_female": "Выбрать девушку 😊"
    }
  },
  "en": {
    "commands": {
      "start": {
        "welcome": "Hello! You have {free_limit} free messages per day."
      }
    },
    "buttons": {
      "choose_female": "Choose girl 😊"
    }
  }
}
```

## Поддерживаемые языки

- **ru** - Русский (по умолчанию)
- **en** - Английский

## Автоматическое определение языка

Система автоматически определяет язык пользователя на основе его настроек Telegram:

- `ru` → Русский
- `en` → Английский  
- `uk`, `be`, `kk` → Русский (ближайший язык)
- Остальные → Русский (по умолчанию)

## Добавление новых переводов

1. Откройте файл `app/shared/i18n/translations.json`
2. Добавьте новый ключ в нужную секцию
3. Добавьте переводы для всех поддерживаемых языков

Пример:
```json
{
  "ru": {
    "new_section": {
      "new_key": "Новый текст на русском"
    }
  },
  "en": {
    "new_section": {
      "new_key": "New text in English"
    }
  }
}
```

## Использование переменных в переводах

Переводы поддерживают форматирование с переменными:

```python
# В JSON
"welcome": "Привет! У тебя {free_limit} бесплатных сообщений в день."

# В коде
i18n.t("commands.start.welcome", free_limit=100)
# Результат: "Привет! У тебя 100 бесплатных сообщений в день."
```

## Fallback механизм

Если перевод не найден для текущего языка, система автоматически использует перевод из языка по умолчанию (русский). Если и там нет перевода, возвращается ключ в квадратных скобках: `[missing.key]`.

## Добавление нового языка

1. Добавьте новый язык в `translations.json`:
```json
{
  "ru": { ... },
  "en": { ... },
  "de": { ... }  // Новый язык
}
```

2. Обновите функцию `get_user_language` в `I18nManager`:
```python
language_mapping = {
    'ru': 'ru',
    'en': 'en',
    'de': 'de',  # Новый язык
    'uk': 'ru',
    'be': 'ru',
    'kk': 'ru',
}
```

## Примеры использования

### В обработчиках команд
```python
@router.message(Command("start"))
async def cmd_start(message: Message, i18n):
    await message.answer(i18n.t("commands.start.welcome", free_limit=100))
```

### В обработчиках callback_query
```python
@router.callback_query(F.data == "gender_female")
async def gender_choice(callback: CallbackQuery, i18n):
    await callback.message.edit_text(i18n.t("gender.changed_to_female"))
```

### В сервисах
```python
from shared.i18n import i18n

class MessageService:
    def get_error_message(self, error_type: str) -> str:
        return i18n.t(f"errors.{error_type}")
```

## Лучшие практики

1. **Используйте описательные ключи**: `commands.start.welcome` вместо `msg1`
2. **Группируйте по функциональности**: все команды в `commands`, все кнопки в `buttons`
3. **Используйте переменные**: для динамических значений используйте `{variable}`
4. **Проверяйте переводы**: убедитесь, что все ключи переведены на все языки
5. **Тестируйте**: проверьте работу с разными языками пользователей
