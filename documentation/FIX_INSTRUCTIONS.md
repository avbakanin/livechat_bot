# 🚨 ПРОБЛЕМА НАЙДЕНА И РЕШЕНИЕ

## ❌ Проблема
Команда `/choose_gender` не работает из-за отсутствия файла `.env` с переменными окружения.

## 🔍 Диагностика
1. **Отсутствует файл .env** - бот не может подключиться к базе данных
2. **Переменные окружения не установлены** - DB_USER, DB_PASSWORD, DB_NAME, TELEGRAM_TOKEN, OPENAI_API_KEY
3. **База данных не настроена** - таблицы могут не существовать

## ✅ Решение

### 1. Создайте файл .env в корне проекта:

```bash
# Database Configuration
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db_name

# Telegram Bot Configuration
TELEGRAM_TOKEN=your_telegram_bot_token

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1

# Payment Configuration (YooKassa) - опционально
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key
```

### 2. Настройте базу данных PostgreSQL:

```bash
# Создайте базу данных
createdb your_db_name

# Выполните SQL скрипт для создания таблиц
psql -d your_db_name -f app/ddl.sql
```

### 3. Получите токены:

- **Telegram Bot Token**: Создайте бота через @BotFather в Telegram
- **OpenAI API Key**: Получите на https://platform.openai.com/api-keys

### 4. Запустите диагностику:

```bash
python diagnose.py
```

### 5. Запустите бота:

```bash
python app/main.py
```

## 🔧 Дополнительные проверки

### Проверьте логи бота:
```bash
tail -f bot.log
```

### Проверьте подключение к базе данных:
```bash
psql -h localhost -U your_db_user -d your_db_name
```

## 📋 Чек-лист

- [ ] Файл .env создан с правильными переменными
- [ ] База данных PostgreSQL запущена
- [ ] Таблицы созданы (выполнен ddl.sql)
- [ ] TELEGRAM_TOKEN получен от @BotFather
- [ ] OPENAI_API_KEY получен с platform.openai.com
- [ ] Диагностика показывает "Все проверки пройдены"
- [ ] Бот запускается без ошибок

## 🎯 После исправления

Команда `/choose_gender` должна работать корректно и показывать клавиатуру выбора пола компаньона.
