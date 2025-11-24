#!/bin/bash

# UnitySphere Quick Launch Script for fan-club.kz

echo "🚀 Запускаем UnitySphere для fan-club.kz..."

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo "🐍 Создаем виртуальное окружение..."
    python3 -m venv venv
fi

# Активация виртуального окружения
echo "🔧 Активируем виртуальное окружение..."
source venv/bin/activate

# Проверка и установка зависимостей
echo "📦 Проверяем зависимости..."
pip list | grep django > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "📥 Устанавливаем Django и зависимости..."
    pip install --upgrade pip
    pip install django djangorestframework django-cors-headers django-filter django-ckeditor psycopg2-binary Pillow beautifulsoup4 pytz openai django-allauth PyJWT cryptography nltk scikit-learn python-magic django-ratelimit bleach gunicorn whitenoise python-dateutil urllib3 requests
fi

# Проверка .env файла
if [ ! -f ".env" ]; then
    echo "⚙️ Создаем .env файл..."
    cat > .env <<EOF
# Django Settings
DJANGO_SECRET_KEY='development-secret-key-not-for-production'
DEBUG=True

# Database Settings (SQLite для development)
DB_NAME=db.sqlite3

# AI Settings
OPENAI_API_KEY=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
OPENAI_MODEL=gpt-4o-mini
SERENA_ENABLED=True
SERENA_URL=http://localhost:8001
SERENA_TIMEOUT=30
AI_CONSULTANT_ENABLED=True

# Email Settings (development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Google OAuth (development)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Redis (если используется)
REDIS_HOST=localhost
REDIS_PORT=6379
EOF
fi

# Проверка Django
echo "✅ Проверяем Django..."
python manage.py check

if [ $? -ne 0 ]; then
    echo "❌ Ошибки Django. Попробуем установить недостающие зависимости..."
    pip install sentence-transformers chromadb
    python manage.py check
fi

# Создание и применение миграций
echo "🗄️ Создаем и применяем миграции..."
python manage.py makemigrations 2>/dev/null || echo "⚠️ Ошибки при создании миграций (возможно AI зависимости)"
python manage.py migrate 2>/dev/null || echo "⚠️ Ошибки при миграции (используем SQLite)"

# Сборка static файлов
echo "📁 Собираем static файлы..."
python manage.py collectstatic --noinput 2>/dev/null || echo "⚠️ Ошибки при сборке static файлов"

# Создание суперпользователя (если нужно)
echo "👤 Проверяем наличие суперпользователя..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Нужно создать суперпользователя')
    exit(1)
else:
    print('Суперпользователь уже существует')
    exit(0)
" 2>/dev/null

if [ $? -eq 1 ]; then
    echo "📝 Создаем суперпользователя..."
    echo "Введите имя пользователя для суперпользователя:"
    read username
    echo "Введите email:"
    read email
    python manage.py createsuperuser --username $username --email $email
fi

# Запуск сервера
echo ""
echo "🎉 Готово! Запускаем сервер..."
echo ""
echo "🌐 Сайт будет доступен по:"
echo "   - Локально: http://localhost:8000"
echo "   - По IP: http://77.243.80.110:8000"
echo "   - Админка: http://localhost:8000/admin/"
echo ""
echo "Нажмите Ctrl+C для остановки сервера"
echo ""

# Запуск сервера
python manage.py runserver 0.0.0.0:8000