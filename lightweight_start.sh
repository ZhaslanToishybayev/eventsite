#!/bin/bash

# 🚀 UnitySphere Lightweight Start Script
# Облегченный запуск Django для сервера с 2GB RAM

echo "🚀 UnitySphere Lightweight Start Script"
echo "========================================"
echo ""

# 1. Полная остановка всех процессов
echo "🛑 Полная остановка всех Django процессов..."
sudo pkill -9 -f "gunicorn" 2>/dev/null
sudo pkill -9 -f "manage.py runserver" 2>/dev/null
sleep 3

# 2. Освобождение порта 8003
echo "🔧 Освобождение порта 8003..."
sudo ss -K sport = 8003 2>/dev/null || true
sudo fuser -k 8003/tcp 2>/dev/null || true
sleep 2

# 3. Проверка порта
echo "🔍 Проверка порта 8003..."
if ss -tln | grep -q ":8003"; then
    echo "⚠️ Порт занят, принудительная остановка..."
    for pid in $(ss -tlnp | grep ":8003" | grep -o "pid=[0-9]*" | cut -d= -f2); do
        if [ ! -z "$pid" ]; then
            sudo kill -9 $pid 2>/dev/null || true
        fi
    done
    sleep 2
fi

if ss -tln | grep -q ":8003"; then
    echo "❌ Порт 8003 не удалось освободить"
    exit 1
else
    echo "✅ Порт 8003 свободен"
fi

# 4. Запуск Django в ОБЛЕГЧЕННОМ режиме
echo "🚀 Запуск Django в облегченном режиме..."
cd /var/www/myapp/eventsite

# Запускаем с минимальным потреблением памяти
nohup /var/www/myapp/eventsite/venv/bin/gunicorn \
    --bind 127.0.0.1:8003 \
    --workers 1 \                # Только 1 воркер (экономия памяти)
    --worker-class sync \        # Синхронный воркер (меньше памяти)
    --worker-connections 50 \    # Меньше соединений
    --timeout 30 \
    --keep-alive 5 \
    --max-requests 500 \         # Раньше перезапускаем воркер
    --max-requests-jitter 50 \
    --limit-request-line 2048 \  # Ограничиваем размер запроса
    --limit-request-field_size 2048 \
    core.wsgi:application > gunicorn.log 2>&1 &

# Сохраняем PID
echo $! > django.pid
echo "📁 PID процесса сохранен в django.pid"

# 5. Долгое ожидание (20 секунд)
echo "⏳ Ожидание запуска Django (20 секунд)..."
sleep 20

# 6. Проверка запуска
echo "🔍 Проверка запуска Django..."
if curl -s http://127.0.0.1:8003/ > /dev/null 2>&1; then
    echo "✅ Django успешно запущен на порту 8003"
else
    echo "⚠️ Django не отвечает напрямую"
fi

# 7. Проверка сайта через nginx
echo "🌐 Проверка сайта через nginx..."
SITE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L http://127.0.0.1/)

if [ "$SITE_STATUS" = "200" ]; then
    echo "✅ Сайт РАБОТАЕТ!"
    echo ""
    echo "📊 Финальный статус:"
    echo "   • Django: ✅ Запущен (1 воркер)"
    echo "   • nginx: ✅ Работает"
    echo "   • Сайт: ✅ Доступен"
    echo "   • Память: ✅ Экономия"
    echo ""
    echo "🎉 UnitySphere работает в облегченном режиме!"
    echo ""
    echo "🛡️ Запуск Auto-Healing системы..."
    /var/www/myapp/eventsite/auto_healing.sh
else
    echo "⚠️ Сайт не работает (код: $SITE_STATUS)"
    echo "💡 Проверьте логи:"
    echo "   - tail -f /var/www/myapp/eventsite/gunicorn.log"
fi