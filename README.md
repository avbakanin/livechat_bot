# Команды для консоли, которые я постоянно забываю

```bash
sudo systemctl restart bot # Перезапускает системный сервис с именем bot
sudo systemctl status bot # Показывает текущее состояние сервиса bot
sudo journalctl -u bot -f # Показывает журнал (логи) сервиса bot в реальном времени
ps aux | grep main.py # Ищет процесс main.py среди всех запущенных процессов
```

# Работа с пакетами Python

## 📦 Управление зависимостями

### Заморозка зависимостей в requirements.txt

```bash
# Заморозить все установленные пакеты
pip freeze > requirements.txt
# Только пакеты, установленные через pip (исключает системные пакеты)
pip list --not-required --format freeze > requirements.txt
# Только пакеты из текущего виртуального окружения
pip freeze --local > requirements.txt
# С сортировкой по алфавиту
pip freeze | sort > requirements.txt
# Умная заморозка (только основные пакеты)
pip freeze | grep -E "(aiogram|openai|python-dotenv|sqlalchemy|asyncpg)" > requirements.txt
```

# 🗣️ Chat Training Server

Серверная часть приложения для развития коммуникативных навыков. Тренируйте общение с искуственным интеллектом в разных ситуациях и с разными компаньонами в безопасной среде.

## 🚀 Возможности

- 💬 Общение с AI-ассистентом (аналогичным ChatGPT)
- 🎯 Режим диалога с AI-ассистентом в смоделированных ситуациях
- 📊 Анализ и feedback по стилю и уверенности в общении
- 🔐 Безопасная анонимная среда

## ⚙️ Установка и запуск

### Предварительные требования

- Python [version]
- PostgreSQL

### Быстрый старт

```bash
# Клонирование репозитория
git clone https://github.com/your-username/chat-training-server.git
cd chat-training-server

# Создание виртуального окружения
python -m venv venv

# Активация (выберите вашу ОС)
source venv/bin/activate      # Linux/Mac
# или
venv\Scripts\activate        # Windows

# Основные зависимости
pip install -r requirements.txt

# Dev-зависимости (линтеры и форматеры)
pip install -r requirements-dev.txt

# Настройка окружения
cp .env.example .env
# Отредактируйте .env файл под ваши настройки

# Запуск сервера
python main.py
```

## Конфигурация

### Базовые настройки

DB_PORT='your-DB-port'
DB_HOST='your-DB-host'
DB_NAME="your-DB-name"
DB_USER="your-user-from-DB"
DB_PASSWORD="your-password-from-DB"
DATABASE_URL=postgresql://user:password@localhost/chat_training

AI_MODEL="your-model-name"

TELEGRAM_TOKEN="your-secret-token-for-sessions"
OPENAI_API_KEY="your-openai-secret-key"

LOG_LEVEL=INFO

# 🛠 Project PoeThePoet Commands

В проекте используется **PoeThePoet** для автоматизации задач по проверке и форматированию кода.

## 🎯 Основные команды

| Команда           | Описание                              | Эмодзи |
| ----------------- | ------------------------------------- | ------ |
| `poe run`         | Запуск бота                           | 🚀     |
| `poe install`     | Установка основных зависимостей       | 📦     |
| `poe dev-install` | Установка dev-зависимостей            | 🔧     |
| `poe update`      | Обновление зависимостей               | 🔄     |
| `poe venv`        | Создание виртуального окружения       | 🏗️     |
| `poe format`      | Форматирование кода                   | ✨     |
| `poe lint`        | Полная проверка кода                  | 🔍     |
| `poe check`       | Проверка без изменений                | 📋     |
| `poe quick-lint`  | Быстрая проверка (критические ошибки) | ⚡     |
| `poe clean`       | Очистка кэша                          | 🧹     |

## 🔄 Составные задачи

| Команда          | Описание                               | Эмодзи |
| ---------------- | -------------------------------------- | ------ |
| `poe setup`      | Установить и запустить                 | 🎯     |
| `poe dev-setup`  | Установить dev-зависимости и запустить | 🛠️     |
| `poe full-check` | Форматирование + проверка              | ✅     |
| `poe restart`    | Перезапуск (очистка + запуск)          | 🔄     |

## 📋 Workflow примеры

```bash
# 🏁 Первая настройка проекта
poe venv          # 🏗️ Создать окружение
poe install       # 📦 Установить зависимости
poe run           # 🚀 Запустить бота

# 🔄 После изменений кода
poe format        # ✨ Отформатировать код
poe check         # 📋 Проверить качество
poe run           # 🚀 Запустить снова

# 💾 Перед коммитом
poe full-check    # ✅ Форматирование + проверка

# 🐛 Если что-то сломалось
poe restart       # 🔄 Очистка + перезапуск
```
