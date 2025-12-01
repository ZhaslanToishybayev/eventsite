#!/bin/bash

# 🚀 МАКСИМАЛЬНО УПРОЩЕННЫЙ ЗАПУСК DJANGO

echo "🚀 МАКСИМАЛЬНО УПРОЩЕННЫЙ ЗАПУСК"
echo "=================================="
echo ""

# Активируем виртуальное окружение
echo "🐍 Активация виртуального окружения..."
source venv/bin/activate

# Проверим базовые настройки
echo ""
echo "🔧 Проверка базовых настроек..."
export DJANGO_SETTINGS_MODULE=core.settings
export PYTHONPATH=/var/www/myapp/eventsite:$PYTHONPATH

python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
try:
    django.setup()
    print('✅ Django setup успешен')
    from django.conf import settings
    print(f'🔧 DEBUG: {settings.DEBUG}')
    print(f'🌐 ALLOWED_HOSTS: {settings.ALLOWED_HOSTS[:3]}...')
    print(f'🗄️ Database: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
    print(f'📋 Tables: {len(settings.INSTALLED_APPS)} приложений')
except Exception as e:
    print(f'❌ Ошибка: {e}')
    import traceback
    traceback.print_exc()
"

# Запустим Django с минимальными параметрами
echo ""
echo "🚀 ЗАПУСК DJANGO..."
echo "==================="
echo ""

echo "📡 Запускаю Django..."
echo "🌐 Попробуем запустить development server..."

# Простой запуск без фонового режима для видимости ошибок
echo "💡 Запускаю Django runserver..."
echo "⚠️ Если видите ошибки ниже - это нормально для диагностики"
echo ""

# Запустим на короткое время для проверки
timeout 5s python manage.py runserver 8000 2>&1 || {
    echo ""
    echo "❌ Django не запустился. Возможные причины:"
    echo "1. Проблемы с зависимостями"
    echo "2. Конфликты в settings"
    echo "3. Проблемы с базой данных"
    echo "4. Ошибки в моделях"
    echo ""
    echo "🔧 Попробуем альтернативные методы..."
}

echo ""
echo "🧪 АЛЬТЕРНАТИВНЫЕ МЕТОДЫ ЗАПУСКА:"
echo "=================================="
echo ""

# Метод 1: Проверим manage.py команды
echo "1. Проверка доступных команд:"
python manage.py help || echo "❌ Проблемы с manage.py"

echo ""
# Метод 2: Проверим базу данных
echo "2. Проверка базы данных:"
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1;')
    print('✅ Подключение к базе работает')
except Exception as e:
    print(f'❌ Ошибка базы: {e}')
"

echo ""
# Метод 3: Проверим конкретные модели
echo "3. Проверка моделей:"
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
try:
    from accounts.models import User
    user_count = User.objects.count()
    print(f'✅ User модель работает: {user_count} пользователей')

    from clubs.models import Club
    club_count = Club.objects.count()
    print(f'✅ Club модель работает: {club_count} клубов')
except Exception as e:
    print(f'❌ Ошибка моделей: {e}')
"

echo ""
echo "🎯 РЕКОМЕНДАЦИИ:"
echo "=================="
echo "1. Проверьте зависимости: pip install -r requirements.txt"
echo "2. Проверьте миграции: python manage.py migrate"
echo "3. Проверьте settings.py на ошибки"
echo "4. Попробуйте запустить с debug=True"
echo ""
echo "💡 Для ручного запуска Django:"
echo "   source venv/bin/activate"
echo "   cd /var/www/myapp/eventsite"
echo "   python manage.py runserver 0.0.0.0:8000"