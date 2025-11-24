#!/bin/bash

# 🎨 ВОССТАНОВЛЕНИЕ ОРИГИНАЛЬНОГО ДИЗАЙНА САЙТА

echo "🎨 ВОССТАНОВЛЕНИЕ ОРИГИНАЛЬНОГО ДИЗАЙНА"
echo "=========================================="

echo "1. Восстановление оригинальных URL-ов..."
cp /var/www/myapp/eventsite/core/urls.py.backup /var/www/myapp/eventsite/core/urls.py

echo ""
echo "2. Проверка структуры приложений..."
echo "Проверка приложений:"
ls -la /var/www/myapp/eventsite/ | grep -E "(accounts|clubs|ai_consultant)" | head -5

echo ""
echo "3. Проверка views и templates..."
echo "Проверка views в clubs:"
if [ -f /var/www/myapp/eventsite/clubs/views.py ]; then
    echo "✅ clubs/views.py найден"
    grep -E "def index\|def home" /var/www/myapp/eventsite/clubs/views.py | head -3
else
    echo "❌ clubs/views.py не найден"
fi

echo ""
echo "Проверка templates..."
if [ -d /var/www/myapp/eventsite/templates ]; then
    echo "✅ templates папка найдена"
    find /var/www/myapp/eventsite/templates -name "*.html" | head -5
else
    echo "❌ templates папка не найдена"
fi

echo ""
echo "4. Проверка URL-ов clubs..."
if [ -f /var/www/myapp/eventsite/clubs/urls.py ]; then
    echo "✅ clubs/urls.py найден"
    cat /var/www/myapp/eventsite/clubs/urls.py
else
    echo "❌ clubs/urls.py не найден"
fi

echo ""
echo "5. Перезапуск Django..."
pkill -f "python.*manage.py.*runserver" || true
sleep 2

cd /var/www/myapp/eventsite
source venv/bin/activate
python manage.py runserver 127.0.0.1:8000 &

echo ""
echo "6. Проверка работы сайта..."
sleep 3
echo "Проверка главной страницы:"
curl -s --connect-timeout 10 https://fan-club.kz | grep -E "<title>|<h1>" | head -3

echo ""
echo "=========================================="
echo "🎨 Оригинальный дизайн восстановлен!"
echo "🌐 Проверьте сайт: https://fan-club.kz"
echo "📋 Теперь доступны: клубы, пользователи, события и т.д."