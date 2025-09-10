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

# Установка зависимостей
pip install -r requirements.txt

# Настройка окружения
cp .env.example .env
# Отредактируйте .env файл под ваши настройки

# Запуск сервера
python main.py
```

## Конфигурация

# Базовые настройки

PORT=8000
HOST=0.0.0.0

# База данных

DATABASE_URL=postgresql://user:password@localhost/chat_training

# AI API ключи (OpenAI или аналоги)

OPENAI_API_KEY=your_openai_api_key_here
AI_MODEL=model_name

# Безопасность

SECRET_KEY=your-secret-key-for-sessions
JWT_SECRET=your-jwt-secret-key

# Логирование

LOG_LEVEL=INFO
