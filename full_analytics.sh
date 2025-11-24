#!/bin/bash

# ПОЛНАЯ АНАЛИТИКА САЙТА fan-club.kz
echo "📊 ПОЛНАЯ АНАЛИТИКА САЙТА fan-club.kz"
echo "============================================"

# 1. Системная информация
echo "🔧 СИСТЕМНАЯ ИНФОРМАЦИЯ:"
echo "ОС: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "Ядро: $(uname -r)"
echo "Архитектура: $(uname -m)"
echo "Время работы: $(uptime -p)"
echo ""

# 2. Проверка всех сервисов
echo "⚙️ СОСТОЯНИЕ СЕРВИСОВ:"
echo "Nginx: $(systemctl is-active nginx 2>/dev/null || echo 'не установлен')"
echo "Django процессы: $(ps aux | grep -c "python.*manage.py.*runserver" || echo '0')"
echo "Python процессы: $(ps aux | grep -c python)"
echo ""

# 3. Сетевая аналитика
echo "🌐 СЕТЕВАЯ АНАЛИТИКА:"
echo "IP адреса сервера:"
ip addr show | grep -E "inet .*brd" | awk '{print $2}' | grep -v "127.0.0.1"
echo ""

echo "Прослушиваемые порты:"
ss -tulpn | grep LISTEN | sort
echo ""

echo "DNS проверка:"
echo "fan-club.kz → $(getent hosts fan-club.kz | cut -d' ' -f1)"
echo "localhost → $(getent hosts localhost | cut -d' ' -f1)"
echo ""

# 4. Django аналитика
echo "🐍 DJANGO АНАЛИТИКА:"
echo "Django процессы:"
ps aux | grep "python.*manage.py.*runserver" | grep -v grep
echo ""

echo "Django ответ:"
curl -s --connect-timeout 3 http://127.0.0.1:8000/ | grep -o "<title>.*</title>" 2>/dev/null || echo "Нет ответа от Django"
echo ""

# 5. Nginx аналитика
echo "/nginx АНАЛИТИКА:"
echo "Nginx конфигурация:"
echo "Включенные сайты:"
ls -la /etc/nginx/sites-enabled/ 2>/dev/null || echo "Nginx не установлен"
echo ""

echo "Nginx логи (последние 5 строк):"
if [ -f /var/log/nginx/fan-club.kz.error.log ]; then
    tail -5 /var/log/nginx/fan-club.kz.error.log 2>/dev/null || echo "Логи недоступны"
else
    echo "Логи не найдены"
fi
echo ""

# 6. Проксирование
echo "🔄 ПРОКСИРОВАНИЕ:"
echo "Nginx → Django:"
curl -s -I http://127.0.0.1 | grep -E "(HTTP|Server|X-Frame-Options)" | head -3
echo ""

# 7. Внешняя доступность
echo "🌍 ВНЕШНЯЯ ДОСТУПНОСТЬ:"
echo "По IP:"
curl -s --connect-timeout 5 -I http://77.243.80.110 | head -1 2>/dev/null || echo "Недоступен по IP"
echo ""

echo "По домену:"
curl -s --connect-timeout 5 -I http://fan-club.kz | head -1 2>/dev/null || echo "Недоступен по домену"
echo ""

# 8. Сравнение ответов
echo "🔍 СРАВНЕНИЕ ОТВЕТОВ:"
echo "127.0.0.1 (localhost):"
curl -s --connect-timeout 3 http://127.0.0.1 | grep -o "<title>.*</title>" | head -1
echo ""

echo "77.243.80.110 (IP):"
curl -s --connect-timeout 3 http://77.243.80.110 | grep -o "<title>.*</title>" | head -1 2>/dev/null || echo "Нет ответа"
echo ""

echo "fan-club.kz (домен):"
curl -s --connect-timeout 3 http://fan-club.kz | grep -o "<title>.*</title>" | head -1 2>/dev/null || echo "Нет ответа"
echo ""

# 9. Проблемы и решения
echo "🚨 АНАЛИЗ ПРОБЛЕМ:"
if ! systemctl is-active --quiet nginx; then
    echo "❌ Nginx не запущен"
fi

if ! ps aux | grep -q "python.*manage.py.*runserver"; then
    echo "❌ Django не запущен"
fi

if ss -tulpn | grep -q ":80.*127.0.0.1:"; then
    echo "⚠️ Nginx слушает только на localhost"
fi

if [ -L /etc/nginx/sites-enabled/default ]; then
    echo "⚠️ Default сайт включен"
fi

if ! curl -s --connect-timeout 3 http://127.0.0.1 > /dev/null; then
    echo "❌ Nginx не отвечает локально"
fi

if ! curl -s --connect-timeout 5 http://77.243.80.110 > /dev/null 2>/dev/null; then
    echo "❌ Сайт недоступен по IP"
fi

# 10. Рекомендации
echo ""
echo "💡 РЕКОМЕНДАЦИИ:"
echo "1. Проверьте, что вы открываете сайт НЕ с этого сервера"
echo "2. Используйте другой браузер или приватное окно"
echo "3. Проверьте hosts файл на вашем компьютере"
echo "4. Отключите VPN/прокси при тестировании"
echo "5. Проверьте через онлайн-сервисы доступности"
echo ""

echo "============================================"
echo "📊 Аналитика завершена"