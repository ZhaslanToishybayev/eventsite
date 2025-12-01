#!/bin/bash

# 🧹 UnitySphere RAM Cleanup Script
# Очистка оперативной памяти

echo "🧹 UnitySphere RAM Cleanup Script"
echo "================================="
echo ""

# 1. Проверяем память ДО очистки
echo "📊 Память ДО очистки:"
free -h
echo ""

# 2. Убиваем старые Django процессы (останется только новый на 8006)
echo "🛑 Убиваем старые Django процессы..."
sudo pkill -9 -f "gunicorn" 2>/dev/null || true
sudo pkill -9 -f "runserver" 2>/dev/null || true
sleep 3

# 3. Запускаем Django на порту 8006 (оставляем только один процесс)
echo "🚀 Запускаем Django на порту 8006..."
cd /var/www/myapp/eventsite
nohup /var/www/myapp/eventsite/venv/bin/python3 manage.py runserver 127.0.0.1:8006 > django_8006.log 2>&1 &

# 4. Освобождаем cache и buffers
echo ""
echo "🧹 Освобождаем cache и buffers..."
sudo sync 2>/dev/null || true
echo 3 | sudo tee /proc/sys/vm/drop_caches 2>/dev/null || true
sleep 2

# 5. Проверяем память ПОСЛЕ очистки
echo ""
echo "📊 Память ПОСЛЕ очистки:"
free -h
echo ""

# 6. Проверяем, что Django работает
echo "🔍 Проверка Django..."
if curl -s http://127.0.0.1:8006/ > /dev/null 2>&1; then
    echo "✅ Django работает на порту 8006"

    # 7. Проверяем сайт через nginx
    echo ""
    echo "🌐 Проверка сайта через nginx..."
    SITE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L http://127.0.0.1/)

    if [ "$SITE_STATUS" = "200" ]; then
        echo "✅ Сайт РАБОТАЕТ через nginx!"
    else
        echo "⚠️ Сайт не работает через nginx (код: $SITE_STATUS)"
        echo "💡 Нужно перенастроить nginx на порт 8006"
        echo "   sudo sed -i 's/server 127.0.0.1:8001;/server 127.0.0.1:8006;/' /etc/nginx/nginx.conf"
        echo "   sudo nginx -s reload"
    fi
else
    echo "⚠️ Django не работает"
fi

echo ""
echo "🎉 RAM cleanup завершен!"
echo ""
echo "💡 Что сделано:"
echo "   • Убиты все старые Django процессы"
echo "   • Запущен один Django на порту 8006"
echo "   • Освобожден cache и buffers"
echo "   • Память оптимизирована"