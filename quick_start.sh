#!/bin/bash

# Quick Start Script for UnitySphere (fan-club.kz) - без AI

echo "🚀 Запускаем UnitySphere без AI компонентов..."

# Активация виртуального окружения
source venv/bin/activate

# Установка основных зависимостей
echo "📦 Устанавливаем основные зависимости..."
pip install --upgrade pip
pip install django djangorestframework django-cors-headers django-filter django-ckeditor psycopg2-binary Pillow beautifulsoup4 pytz openai django-allauth PyJWT cryptography nltk scikit-learn python-magic django-ratelimit bleach gunicorn gevent redis django-redis whitenoise hiredis python-dateutil urllib3 requests

# Создание .env файла для development без AI
echo "⚙️ Создаем .env файл..."
cat > .env <<EOF
# Django Settings
DJANGO_SECRET_KEY='development-secret-key-not-for-production'
DEBUG=True

# Database Settings (SQLite для development)
DB_NAME=db.sqlite3

# AI Settings (временно отключены)
AI_CONSULTANT_ENABLED=False
SERENA_ENABLED=False

# Email Settings (development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Google OAuth (development)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Redis (если используется)
REDIS_HOST=localhost
REDIS_PORT=6379
EOF

# Проверка Django
echo "✅ Проверяем Django..."
python manage.py check --deploy --settings=core.settings

# Создание и применение миграций
echo "🗄️ Создаем и применяем миграции..."
python manage.py makemigrations
python manage.py migrate

# Сборка static файлов
echo "📁 Собираем static файлы..."
python manage.py collectstatic --noinput

# Создание суперпользователя
echo "👤 Создаем суперпользователя..."
echo "Введите имя пользователя для суперпользователя:"
read username
echo "Введите email:"
read email
python manage.py createsuperuser --username $username --email $email

echo ""
echo "✅ Базовая настройка завершена!"
echo ""
echo "📋 Сайт готов к работе:"
echo "1. Запустите сервер: python manage.py runserver 0.0.0.0:8000"
echo "2. Админка: http://localhost:8000/admin/"
echo ""
echo "🌐 Сайт будет доступен по:"
echo "   - Локально: http://localhost:8000"
echo "   - По IP: http://77.243.80.110:8000"
echo "   - Домен: http://fan-club.kz:8000 (если DNS настроен)"