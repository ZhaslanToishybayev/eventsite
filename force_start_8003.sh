#!/bin/bash

# 🚀 UnitySphere Force Start Script (Port 8003)
# Принудительный запуск Django на порту 8003

echo "🚀 UnitySphere Force Start Script (Port 8003)"
echo "=============================================="
echo ""

# 1. Жесткая остановка всех процессов
echo "🛑 Жесткая остановка всех Django процессов..."
sudo pkill -9 -f "gunicorn" 2>/dev/null
sudo pkill -9 -f "manage.py runserver" 2>/dev/null
sleep 3

# 2. Принудительное освобождение порта 8003
echo "🔧 Принудительное освобождение порта 8003..."
sudo ss -K sport = 8003 2>/dev/null || true
sudo fuser -k 8003/tcp 2>/dev/null || true
sleep 2

# 3. Проверка, что порт свободен
echo "🔍 Проверка порта 8003..."
if ss -tln | grep -q ":8003"; then
    echo "⚠️ Порт 8003 все еще занят, принудительная остановка..."
    # Найдем и убьем конкретные процессы
    for pid in $(ss -tlnp | grep ":8003" | grep -o "pid=[0-9]*" | cut -d= -f2); do
        if [ ! -z "$pid" ]; then
            sudo kill -9 $pid 2>/dev/null || true
        fi
    done
    sleep 2
fi

# 4. Проверка окончательного освобождения
if ss -tln | grep -q ":8003"; then
    echo "❌ Порт 8003 не удалось освободить"
    echo "💡 Попробуйте перезагрузить сервер"
    exit 1
else
    echo "✅ Порт 8003 свободен"
fi

# 5. Запуск Django на порту 8003
echo "🚀 Запуск Django на порту 8003..."
cd /var/www/myapp/eventsite

# Запускаем с надежными параметрами
nohup /var/www/myapp/eventsite/venv/bin/gunicorn \
    --bind 127.0.0.1:8003 \
    --workers 2 \
    --timeout 30 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --worker-class sync \
    --worker-connections 100 \
    core.wsgi:application > gunicorn.log 2>&1 &

# Сохраняем PID процесса
echo $! > django.pid
echo "📁 PID процесса сохранен в django.pid"

# 6. Долгое ожидание запуска (15 секунд)
echo "⏳ Ожидание запуска Django (15 секунд)..."
sleep 15

# 7. Проверка запуска
echo "🔍 Проверка запуска Django..."
if curl -s http://127.0.0.1:8003/ > /dev/null 2>&1; then
    echo "✅ Django успешно запущен на порту 8003"
else
    echo "⚠️ Django не отвечает напрямую, но может работать через nginx"
fi

# 8. Проверка сайта через nginx
echo "🌐 Проверка сайта через nginx..."
SITE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L http://127.0.0.1/)

if [ "$SITE_STATUS" = "200" ]; then
    echo "✅ Сайт РАБОТАЕТ!"
    echo ""
    echo "📊 Финальный статус:"
    echo "   • Django: ✅ Запущен на порту 8003"
    echo "   • nginx: ✅ Работает"
    echo "   • Сайт: ✅ Доступен"
    echo "   • Login: $(curl -s -o /dev/null -w "%{http_code}" -L http://127.0.0.1/accounts/login/ 2>&1)"
    echo "   • Google OAuth: $(curl -s -o /dev/null -w "%{http_code}" -L http://127.0.0.1/accounts/google/login/ 2>&1)"
    echo "   • Единомышленники: $(curl -s -o /dev/null -w "%{http_code}" -L http://127.0.0.1/accounts/ 2>&1)"
    echo ""
    echo "🎉 UnitySphere стабильно работает!"
    echo ""
    echo "🛡️ Запуск Auto-Healing системы..."
    /var/www/myapp/eventsite/auto_healing.sh
else
    echo "⚠️ Сайт не работает (код: $SITE_STATUS)"
    echo "💡 Проверьте логи:"
    echo "   - tail -f /var/www/myapp/eventsite/gunicorn.log"
    echo "   - sudo journalctl -u nginx -f"
fi