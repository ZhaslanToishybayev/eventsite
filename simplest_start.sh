#!/bin/bash

# 🚀 UnitySphere Simplest Start Script
# Самый простой запуск Django

echo "🚀 UnitySphere Simplest Start Script"
echo "===================================="
echo ""

# 1. Убиваем все процессы
echo "🛑 Убиваем все Django процессы..."
sudo pkill -9 -f "gunicorn" 2>/dev/null
sudo pkill -9 -f "runserver" 2>/dev/null
sleep 5

# 2. Освобождаем память
echo "🧹 Освобождение памяти..."
sudo sync 2>/dev/null || true
echo 3 | sudo tee /proc/sys/vm/drop_caches 2>/dev/null || true
sleep 3

# 3. Проверяем память
echo "📊 Проверка памяти..."
free -h

# 4. Проверяем порт 8005
echo "🔍 Проверка порта 8005..."
if ss -tln | grep -q ":8005"; then
    echo "⚠️ Порт 8005 занят"
    exit 1
else
    echo "✅ Порт 8005 свободен"
fi

# 5. Запускаем Django самым простым способом
echo "🚀 Запуск Django (самый простой способ)..."
cd /var/www/myapp/eventsite

# Просто запускаем manage.py runserver без лишних параметров
nohup /var/www/myapp/eventsite/venv/bin/python3 manage.py runserver 127.0.0.1:8006 > simplest.log 2>&1 &

# Сохраняем PID
echo $! > simplest.pid
echo "📁 PID процесса сохранен в simplest.pid"

# 6. Ждем 40 секунд (очень долго для полной загрузки)
echo "⏳ Ожидание полной загрузки Django (40 секунд)..."
sleep 40

# 7. Проверка запуска
echo "🔍 Проверка запуска Django..."
if curl -s http://127.0.0.1:8006/ > /dev/null 2>&1; then
    echo "✅ Django успешно запущен"

    # 8. Проверка сайта через nginx
    echo "🌐 Проверка сайта через nginx..."
    SITE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L http://127.0.0.1/)

    if [ "$SITE_STATUS" = "200" ]; then
        echo "✅ Сайт РАБОТАЕТ!"
        echo ""
        echo "🎉 UnitySphere работает!"
        echo ""
        echo "🛡️ Рекомендуется запустить Auto-Healing:"
        echo "   /var/www/myapp/eventsite/auto_healing.sh"
    else
        echo "⚠️ Сайт не работает через nginx (код: $SITE_STATUS)"
        echo "💡 Проверьте nginx конфигурацию"
    fi
else
    echo "⚠️ Django не отвечает напрямую"
    echo "💡 Проверьте логи: tail -f /var/www/myapp/eventsite/simplest.log"

    # Проверим, может Django запустился, но медленно отвечает
    echo "⏳ Проверка через 10 секунд..."
    sleep 10
    if curl -s http://127.0.0.1:8006/ > /dev/null 2>&1; then
        echo "✅ Django ответил через 10 секунд"
        echo "🌐 Проверка сайта через nginx..."
        SITE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L http://127.0.0.1/)
        if [ "$SITE_STATUS" = "200" ]; then
            echo "✅ Сайт РАБОТАЕТ!"
        else
            echo "⚠️ Сайт не работает (код: $SITE_STATUS)"
        fi
    else
        echo "❌ Django не ответил даже через 10 секунд"
    fi
fi

echo ""
echo "💡 Этот скрипт использует самый простой способ:"
echo "   • python manage.py runserver (без Gunicorn)"
echo "   • production settings (все приложения)"
echo "   • Минимум процессов"
echo "   • Максимум времени на загрузку"