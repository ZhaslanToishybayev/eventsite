#!/bin/bash

# 🚀 UnitySphere Development Server Start Script
# Запуск Django через manage.py runserver (меньше памяти)

echo "🚀 UnitySphere Development Server Start Script"
echo "==============================================="
echo ""

# 1. Останавливаем все Gunicorn процессы
echo "🛑 Остановка всех Gunicorn процессов..."
sudo pkill -f "gunicorn" 2>/dev/null
sleep 3

# 2. Запускаем Django через manage.py runserver
echo "🚀 Запуск Django через manage.py runserver..."
cd /var/www/myapp/eventsite

# Запускаем development server (потребляет меньше памяти)
nohup /var/www/myapp/eventsite/venv/bin/python3 manage.py runserver 127.0.0.1:8005 > django_runserver.log 2>&1 &

# Сохраняем PID
echo $! > django_runserver.pid
echo "📁 PID процесса сохранен в django_runserver.pid"

# 3. Ждем 20 секунд
echo "⏳ Ожидание запуска Django (20 секунд)..."
sleep 20

# 4. Проверка запуска
echo "🔍 Проверка запуска Django через runserver..."
if curl -s http://127.0.0.1:8005/ > /dev/null 2>&1; then
    echo "✅ Django успешно запущен через runserver"
else
    echo "⚠️ Django не отвечает напрямую"
fi

# 5. Проверка сайта через nginx
echo "🌐 Проверка сайта через nginx..."
SITE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L http://127.0.0.1/)

if [ "$SITE_STATUS" = "200" ]; then
    echo "✅ Сайт РАБОТАЕТ!"
    echo ""
    echo "📊 Финальный статус:"
    echo "   • Django: ✅ Запущен через runserver"
    echo "   • nginx: ✅ Работает"
    echo "   • Сайт: ✅ Доступен"
    echo ""
    echo "🎉 UnitySphere работает через development server!"
    echo ""
    echo "💡 Development server потребляет меньше памяти чем Gunicorn"
    echo "   • Подходит для 2GB RAM"
    echo "   • Автоматическое обновление кода"
    echo "   • Простая диагностика"
else
    echo "⚠️ Сайт не работает (код: $SITE_STATUS)"
    echo "💡 Проверьте логи: tail -f /var/www/myapp/eventsite/django_runserver.log"
    echo ""
    echo "🔧 Если не работает:"
    echo "   1. Проверьте свободную память: free -h"
    echo "   2. Убедитесь, что порт 8005 свободен"
    echo "   3. Попробуйте перезагрузить сервер"
fi