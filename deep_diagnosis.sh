#!/bin/bash

# Глубокая диагностика сайта fan-club.kz

echo "🔍 ГЛУБОКАЯ ДИАГНОСТИКА САЙТА fan-club.kz"
echo "=============================================="

echo "1. Проверка Django сервера..."
if ps aux | grep -q "python.*manage.py.*runserver"; then
    echo "✅ Django процессы запущены"
    curl -s --connect-timeout 3 http://127.0.0.1:8000 > /dev/null && echo "✅ Django отвечает на 127.0.0.1:8000" || echo "❌ Django не отвечает"
else
    echo "❌ Django процессы не найдены"
fi

echo ""
echo "2. Проверка Nginx..."
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx запущен"
    curl -s --connect-timeout 3 http://127.0.0.1 > /dev/null && echo "✅ Nginx отвечает на localhost" || echo "❌ Nginx не отвечает на localhost"
else
    echo "❌ Nginx не запущен"
fi

echo ""
echo "3. Проверка сетевых соединений..."
if ss -tulpn | grep -q ":80.*0.0.0.0"; then
    echo "✅ Nginx слушает на всех интерфейсах (0.0.0.0:80)"
else
    echo "❌ Nginx не слушает на всех интерфейсах"
fi

if ss -tulpn | grep -q ":8000.*127.0.0.1"; then
    echo "✅ Django слушает на 127.0.0.1:8000"
else
    echo "❌ Django не слушает на 127.0.0.1:8000"
fi

echo ""
echo "4. Проверка конфигурации Nginx..."
if [ -L /etc/nginx/sites-enabled/default ]; then
    echo "❌ Default сайт ВКЛЮЧЕН в Nginx (это проблема!)"
else
    echo "✅ Default сайт отключен"
fi

if [ -L /etc/nginx/sites-enabled/fan-club.kz ]; then
    echo "✅ Конфигурация fan-club.kz включена"
else
    echo "❌ Конфигурация fan-club.kz не включена"
fi

echo ""
echo "5. Проверка DNS..."
if ping -c 1 -W 1 fan-club.kz > /dev/null 2>&1; then
    echo "✅ DNS работает: fan-club.kz → $(getent hosts fan-club.kz | cut -d' ' -f1)"
else
    echo "❌ DNS не работает"
fi

echo ""
echo "6. Проверка доступности по IP..."
if curl -s --connect-timeout 5 http://77.243.80.110 > /dev/null 2>&1; then
    echo "✅ Сайт доступен по IP адресу"
else
    echo "❌ Сайт недоступен по IP адресу"
fi

echo ""
echo "7. Проверка ответа сервера..."
echo "Локально (через Nginx):"
curl -s -I http://127.0.0.1 | head -1

echo "По IP:"
curl -s -I http://77.243.80.110 | head -1 2>/dev/null || echo "Нет ответа"

echo ""
echo "8. Проверка содержимого..."
echo "Проверка содержимого локально:"
curl -s http://127.0.0.1 | grep -o "<title>.*</title>" | head -1

echo ""
echo "=============================================="
echo "🔍 Диагностика завершена"