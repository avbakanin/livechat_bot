# 🗑️ Обновление команды: /stop → /delete_me

## 📋 Обзор изменений

Команда `/stop` была переименована в `/delete_me` с обновленными сообщениями, которые четко указывают на полное удаление данных пользователя, включая подписку Premium.

## 🔄 Что было изменено

### **1. Константы команд**
**Файл:** `app/shared/constants/commands.py`

**Изменения:**
```python
# ДО:
STOP_CONFIRM = "stop_confirm"
STOP_CANCEL = "stop_cancel"
STOP = "stop"

# ПОСЛЕ:
DELETE_ME_CONFIRM = "delete_me_confirm"
DELETE_ME_CANCEL = "delete_me_cancel"
DELETE_ME = "delete_me"
```

### **2. Обработчики команд**
**Файл:** `app/domain/user/handlers.py`

**Изменения:**
```python
# ДО:
@router.message(Command(commands=[BotCommands.STOP]))
async def cmd_stop(message: Message, i18n: I18nMiddleware, cached_user: UserCacheData = None):

# ПОСЛЕ:
@router.message(Command(commands=[BotCommands.DELETE_ME]))
async def cmd_delete_me(message: Message, i18n: I18nMiddleware, cached_user: UserCacheData = None):
```

### **3. Callback обработчики**
**Файл:** `app/domain/user/callbacks.py`

**Изменения:**
```python
# ДО:
@router.callback_query(F.data == Callbacks.STOP_CONFIRM)
async def stop_confirm(callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware):

@router.callback_query(F.data == Callbacks.STOP_CANCEL)
async def stop_cancel(callback: CallbackQuery, i18n: I18nMiddleware):

# ПОСЛЕ:
@router.callback_query(F.data == Callbacks.DELETE_ME_CONFIRM)
async def delete_me_confirm(callback: CallbackQuery, user_service: UserService, i18n: I18nMiddleware):

@router.callback_query(F.data == Callbacks.DELETE_ME_CANCEL)
async def delete_me_cancel(callback: CallbackQuery, i18n: I18nMiddleware):
```

### **4. Клавиатуры**
**Файл:** `app/domain/user/keyboards.py`

**Изменения:**
```python
# ДО:
def get_stop_confirmation_keyboard() -> InlineKeyboardMarkup:
    InlineKeyboardButton(text=i18n.t("buttons.yes"), callback_data=Callbacks.STOP_CONFIRM),
    InlineKeyboardButton(text=i18n.t("buttons.no"), callback_data=Callbacks.STOP_CANCEL),

# ПОСЛЕ:
def get_delete_me_confirmation_keyboard() -> InlineKeyboardMarkup:
    InlineKeyboardButton(text=i18n.t("buttons.yes"), callback_data=Callbacks.DELETE_ME_CONFIRM),
    InlineKeyboardButton(text=i18n.t("buttons.no"), callback_data=Callbacks.DELETE_ME_CANCEL),
```

## 🌍 Обновления переводов

### **Все 9 языков обновлены:**
- 🇷🇺 **Русский** (ru)
- 🇺🇸 **Английский** (en)
- 🇪🇸 **Испанский** (es)
- 🇫🇷 **Французский** (fr)
- 🇩🇪 **Немецкий** (de)
- 🇮🇹 **Итальянский** (it)
- 🇵🇱 **Польский** (pl)
- 🇷🇸 **Сербский** (sr)
- 🇹🇷 **Турецкий** (tr)

### **Ключи переводов изменены:**
```json
// ДО:
"stop": {
  "confirmation": "...",
  "success": "...",
  "cancelled": "...",
  "already_stopped": "..."
}

// ПОСЛЕ:
"delete_me": {
  "confirmation": "...",
  "success": "...",
  "cancelled": "...",
  "already_stopped": "..."
}
```

### **Команды в справке:**
```json
// ДО:
"stop_command": "/stop - Остановить бота"

// ПОСЛЕ:
"delete_me_command": "/delete_me - Полное удаление данных"
```

## 📝 Новые сообщения

### **🇷🇺 Русский:**

#### **Подтверждение:**
```
🗑️ Полное удаление данных

Вы уверены, что хотите полностью удалить все свои данные?

Будут удалены БЕЗВОЗВРАТНО:
• История переписки
• Настройки
• Подписка Premium
• Кэш
• Все персональные данные

⚠️ Это действие нельзя отменить!

💡 Если захотите вернуться, нажмите /start
```

#### **Успех:**
```
👋 Данные удалены

Все ваши данные полностью удалены из системы.

💡 Если захотите вернуться, нажмите /start

😢 Нам жаль, что вы уходите. Мы будем ждать вашего возвращения!
```

### **🇺🇸 Английский:**

#### **Подтверждение:**
```
🗑️ Complete Data Deletion

Are you sure you want to completely delete all your data?

Will be deleted PERMANENTLY:
• Chat history
• Settings
• Premium Subscription
• Cache
• All personal data

⚠️ This action cannot be undone!

💡 If you want to return, press /start
```

#### **Успех:**
```
👋 Data Deleted

All your data has been completely deleted from the system.

💡 If you want to return, press /start

😢 We're sorry to see you go. We'll be waiting for your return!
```

## 🎯 Ключевые улучшения

### **1. Четкость названия:**
- **ДО:** `/stop` - неясно, что именно останавливается
- **ПОСЛЕ:** `/delete_me` - четко указывает на удаление данных

### **2. Подчеркивание важности:**
- ✅ **Выделена подписка Premium** жирным шрифтом
- ✅ **Указано "БЕЗВОЗВРАТНО"** на всех языках
- ✅ **Предупреждение о необратимости** действия

### **3. Инструкция по возврату:**
- ✅ **Добавлено "Если захотите вернуться, нажмите /start"**
- ✅ **Во всех сообщениях** (подтверждение и успех)
- ✅ **На всех языках**

### **4. Визуальные улучшения:**
- ✅ **Эмодзи 🗑️** вместо 🛑 (более подходящий для удаления)
- ✅ **Структурированный текст** с четкими разделами
- ✅ **Выделение важных элементов** жирным шрифтом

## 📊 Функциональность

### **Команда работает идентично /stop:**
1. **Диалог подтверждения** с подробным описанием
2. **Полное удаление пользователя** из БД
3. **Очистка кэша** FSM
4. **Сообщение об успехе** с инструкцией по возврату

### **Безопасность:**
- ✅ **Защита от повторного запуска** (проверка флага `is_stopped`)
- ✅ **Исправлена ошибка кэша** (обновление перед удалением)
- ✅ **Четкие предупреждения** о необратимости

## 🔄 Совместимость

### **Обновленные файлы:**
- ✅ **Константы** - новые callback данные
- ✅ **Обработчики** - новые функции
- ✅ **Клавиатуры** - новые callback данные
- ✅ **Переводы** - новые ключи для всех языков
- ✅ **Справка** - обновленная команда

### **Обратная совместимость:**
- ❌ **Старые команды не работают** (это правильно)
- ✅ **Новые команды работают** корректно
- ✅ **Все функции сохранены**

## 🎉 Результат

### **Пользователи теперь получают:**
1. **Четкое понимание** того, что делает команда
2. **Предупреждение о потере Premium** подписки
3. **Инструкции по возврату** в систему
4. **Профессиональный интерфейс** с правильными эмодзи

### **Команда стала более:**
- 📝 **Понятной** - название отражает действие
- ⚠️ **Предупреждающей** - четкие предупреждения
- 💡 **Полезной** - инструкции по возврату
- 🌍 **Интернациональной** - качественные переводы

**Обновление успешно завершено! Команда `/delete_me` готова к использованию.** ✅
