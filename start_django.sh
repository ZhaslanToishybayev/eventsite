#!/bin/bash

# 🚀 Django Quick Start Script
# Быстрый запуск Django на порту 8003

echo "🚀 Запуск Django на порту 8003..."

# Останавливаем старые процессы (если есть права)
sudo pkill -f "gunicorn" 2>/dev/null
sudo pkill -f "manage.py runserver" 2>/dev/null
sleep 3

# Запускаем Django
cd /var/www/myapp/eventsite
nohup /var/www/myapp/eventsite/venv/bin/gunicorn --bind 127.0.0.1:8003 --workers 2 --timeout 30 --keep-alive 5 core.wsgi:application > gunicorn.log 2>&1 &

# Ждем 5 секунд
sleep 5

# Проверяем
if curl -s http://127.0.0.1:8003/ > /dev/null 2>&1; then
    echo "✅ Django запущен на порту 8003"
else
    echo "❌ Django не запустился на порту 8003"
    echo "📋 Проверьте логи: tail -f /var/www/myapp/eventsite/gunicorn.log"
fi

# Проверяем сайт
if curl -s -o /dev/null -w "%{http_code}" -L http://127.0.0.1/ | grep -q "200"; then
    echo "✅ Сайт РАБОТАЕТ"
else
    echo "⚠️ Сайт не работает"
fi