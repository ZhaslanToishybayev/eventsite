#!/bin/bash

# 🚀 UnitySphere Minimal Django Start Script
# Запуск Django в minimal режиме (максимальная экономия памяти)

echo "🚀 UnitySphere Minimal Django Start Script"
echo "==========================================="
echo ""

# 1. Освобождаем память
echo "🧹 Освобождение памяти..."
sudo pkill -9 -f "gunicorn" 2>/dev/null
sudo pkill -9 -f "runserver" 2>/dev/null
sudo sync 2>/dev/null || true
echo 3 | sudo tee /proc/sys/vm/drop_caches 2>/dev/null || true
sleep 3

# 2. Проверяем память
echo "📊 Проверка памяти..."
free -h

# 3. Создаем minimal settings
echo "🔧 Создание minimal settings..."
cd /var/www/myapp/eventsite

# Создаем временный minimal settings
cat > core/minimal_settings.py << 'EOF'
"""
Minimal Django settings for low memory usage
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-minimal-key-for-low-memory'
DEBUG = False
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'clubs',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Minimal cache (no cache)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Minimal logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
EOF

echo "✅ Minimal settings создан"

# 4. Запускаем Django в minimal режиме
echo "🚀 Запуск Django в minimal режиме..."
nohup /var/www/myapp/eventsite/venv/bin/python3 manage.py runserver 127.0.0.1:8005 --settings=core.minimal_settings > minimal_django.log 2>&1 &

# Сохраняем PID
echo $! > minimal_django.pid
echo "📁 PID процесса сохранен в minimal_django.pid"

# 5. Ждем 20 секунд
echo "⏳ Ожидание запуска Django (20 секунд)..."
sleep 20

# 6. Проверка запуска
echo "🔍 Проверка запуска Django в minimal режиме..."
if curl -s http://127.0.0.1:8005/ > /dev/null 2>&1; then
    echo "✅ Django успешно запущен в minimal режиме"

    # 7. Проверка сайта через nginx
    echo "🌐 Проверка сайта через nginx..."
    SITE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L http://127.0.0.1/)

    if [ "$SITE_STATUS" = "200" ]; then
        echo "✅ Сайт РАБОТАЕТ в minimal режиме!"
        echo ""
        echo "📊 Финальный статус:"
        echo "   • Django: ✅ Запущен в minimal режиме"
        echo "   • nginx: ✅ Работает"
        echo "   • Сайт: ✅ Доступен"
        echo "   • Память: ✅ Минимальное потребление"
        echo ""
        echo "🎉 UnitySphere работает в minimal режиме!"
        echo ""
        echo "💡 Minimal режим:"
        echo "   • Только необходимые приложения"
        echo "   • Нет кэширования"
        echo "   • Простой runserver"
        echo "   • Минимум middleware"
        echo ""
        echo "⚠️ Это временный режим для проверки работоспособности"
        echo "   Для production нужно больше RAM или оптимизация"
    else
        echo "⚠️ Сайт не работает через nginx (код: $SITE_STATUS)"
        echo "💡 Но Django работает, проверьте напрямую: http://127.0.0.1:8005/"
    fi
else
    echo "⚠️ Django не отвечает напрямую"
    echo "💡 Проверьте логи: tail -f /var/www/myapp/eventsite/minimal_django.log"
fi

echo ""
echo "🔧 Для возврата к production settings:"
echo "   rm core/minimal_settings.py"
echo "   pkill -f runserver"
echo "   Запустите обычный скрипт запуска"