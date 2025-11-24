#!/bin/bash

# Simple Setup Script for UnitySphere (fan-club.kz) - без sudo

echo "🚀 Начинаем упрощенную настройку..."

# 1. Создание виртуального окружения
echo "🐍 Создаем виртуальное окружение..."
python3 -m venv venv

# 2. Активация виртуального окружения
source venv/bin/activate

# 3. Установка зависимостей
echo "📦 Устанавливаем зависимости..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements.production.txt

# 4. Создание .env файла для development
echo "⚙️ Создаем .env файл для development..."
cat > .env <<EOF
# Django Settings
DJANGO_SECRET_KEY='development-secret-key-not-for-production'
DEBUG=True

# Database Settings (SQLite для development)
DB_NAME=db.sqlite3

# AI Settings
OPENAI_API_KEY=your-openai-api-key-here
SERENA_ENABLED=True
SERENA_URL=http://localhost:8001
SERENA_TIMEOUT=30
AI_CONSULTANT_ENABLED=True

# Email Settings (development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Google OAuth (development)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Anthropic AI
ANTHROPIC_API_KEY=sk-your-anthropic-key

# Redis (если используется)
REDIS_HOST=localhost
REDIS_PORT=6379
EOF

# 5. Проверка Django
echo "✅ Проверяем Django..."
python manage.py check

# 6. Создание и применение миграций
echo "🗄️ Создаем миграции..."
python manage.py makemigrations
python manage.py migrate

# 7. Сборка статических файлов
echo "📁 Собираем static файлы..."
python manage.py collectstatic --noinput

# 8. Создание суперпользователя (интерактивно)
echo "👤 Создаем суперпользователя..."
echo "Запустите: python manage.py createsuperuser"
echo "Или: source venv/bin/activate && python manage.py createsuperuser"

echo ""
echo "✅ Базовая настройка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Запустите сервер: python manage.py runserver 0.0.0.0:8000"
echo "2. Создайте суперпользователя: python manage.py createsuperuser"
echo "3. Настройте Nginx конфигурацию"
echo "4. Настройте ИИ-серверы"
echo ""
echo "🌐 Сайт будет доступен по:"
echo "   - Локально: http://localhost:8000"
echo "   - По IP: http://77.243.80.110:8000"
echo "   - Домен: http://fan-club.kz:8000 (если DNS настроен)"