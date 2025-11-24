#!/bin/bash

# СВЕРХГЛУБОКИЙ АНАЛИЗ - ИЩЕМ СКРЫТЫЕ ПРОБЛЕМЫ
echo "🔍 СВЕРХГЛУБОКИЙ АНАЛИЗ САЙТА fan-club.kz"
echo "==============================================="

echo "1. Проверка нестандартных проблем..."

# Проверка на наличие нескольких Nginx конфигураций
echo "📋 Конфигурации Nginx:"
echo "sites-available:"
ls -la /etc/nginx/sites-available/ 2>/dev/null | grep fan-club
echo "sites-enabled:"
ls -la /etc/nginx/sites-enabled/ 2>/dev/null
echo ""

# Проверка конфигурации fan-club.kz
echo "📄 Содержимое fan-club.kz:"
if [ -f /etc/nginx/sites-available/fan-club.kz ]; then
    grep -E "(listen|server_name|proxy_pass)" /etc/nginx/sites-available/fan-club.kz
else
    echo "❌ Файл конфигурации не найден!"
fi
echo ""

# Проверка на наличие других виртуальных хостов
echo "🌐 Другие виртуальные хосты:"
grep -r "server_name.*fan-club" /etc/nginx/ 2>/dev/null || echo "Других конфигураций не найдено"
echo ""

# Проверка на наличие redirect/rewrite правил
echo "🔄 Redirect/rewrite правила:"
grep -r "return\|rewrite\|redirect" /etc/nginx/sites-enabled/ 2>/dev/null || echo "Правил не найдено"
echo ""

# Проверка логов на ошибки
echo "📋 Анализ логов Nginx:"
if [ -f /var/log/nginx/error.log ]; then
    echo "Последние ошибки Nginx:"
    tail -10 /var/log/nginx/error.log | grep -E "(fan-club|error|failed)" | tail -5
else
    echo "Логи Nginx не найдены"
fi
echo ""

# Проверка на наличие SSL/TLS проблем
echo "🔒 SSL/TLS конфигурация:"
if [ -f /etc/nginx/sites-available/fan-club.kz ]; then
    grep -i "ssl\|https\|443" /etc/nginx/sites-available/fan-club.kz || echo "SSL не настроен"
fi
echo ""

# Проверка на наличие geoip/ограничений
echo "🌍 GeoIP/ограничения:"
if [ -f /etc/nginx/sites-available/fan-club.kz ]; then
    grep -E "deny\|allow\|geo" /etc/nginx/sites-available/fan-club.kz || echo "Ограничений не найдено"
fi
echo ""

# Проверка на наличие rate limiting
echo "⚡ Rate limiting:"
if [ -f /etc/nginx/sites-available/fan-club.kz ]; then
    grep -i "limit" /etc/nginx/sites-available/fan-club.kz || echo "Rate limiting не найден"
fi
echo ""

# Проверка настройки Django
echo "🐍 Django настройки:"
echo "DEBUG режим:"
grep "DEBUG" /var/www/myapp/eventsite/core/settings.py 2>/dev/null | head -1 || echo "Не удалось проверить"
echo ""

echo "ALLOWED_HOSTS:"
grep -A 5 "ALLOWED_HOSTS" /var/www/myapp/eventsite/core/settings.py 2>/dev/null || echo "Не найдено"
echo ""

# Проверка статических файлов
echo "📁 Статические файлы:"
if [ -d /var/www/myapp/eventsite/staticfiles ]; then
    echo "Статические файлы: $(ls -1 /var/www/myapp/eventsite/staticfiles | wc -l) файлов"
else
    echo "❌ Папка staticfiles не найдена"
fi

if [ -d /var/www/myapp/eventsite/media ]; then
    echo "Media файлы: $(ls -1 /var/www/myapp/eventsite/media | wc -l) файлов"
else
    echo "❌ Папка media не найдена"
fi
echo ""

# Проверка на наличие проблем с URL routing
echo "🔗 URL Routing:"
echo "Проверка Django URL конфигурации..."
if [ -f /var/www/myapp/eventsite/core/urls.py ]; then
    grep -E "(fan-club|home|urlpatterns)" /var/www/myapp/eventsite/core/urls.py | head -3
else
    echo "❌ urls.py не найден"
fi
echo ""

# Проверка на наличие проблем с базой данных
echo "💾 База данных:"
if [ -f /var/www/myapp/eventsite/db.sqlite3 ]; then
    echo "SQLite: $(ls -lh /var/www/myapp/eventsite/db.sqlite3 | awk '{print $5}')"
    sqlite3 /var/www/myapp/eventsite/db.sqlite3 "SELECT name FROM sqlite_master WHERE type='table' LIMIT 5;" 2>/dev/null || echo "Ошибка чтения БД"
else
    echo "SQLite не найдена"
fi
echo ""

# Проверка переменных окружения
echo "⚙️ Переменные окружения:"
if [ -f /var/www/myapp/eventsite/.env ]; then
    echo "Переменные окружения найдены:"
    grep -E "(DEBUG|SECRET|HOST|ALLOWED)" /var/www/myapp/eventsite/.env | head -5
else
    echo "❌ .env файл не найден"
fi
echo ""

# Проверка на наличие проблем с процессами
echo "🔄 Процессы:"
echo "Django процессы:"
ps aux | grep "python.*manage.py" | grep -v grep
echo ""

echo "Nginx процессы:"
ps aux | grep nginx | grep -v grep
echo ""

# Проверка сетевых проблем
echo "🌐 Сетевые проблемы:"
echo "Routing table:"
ip route | grep default
echo ""

echo "DNS серверы:"
cat /etc/resolv.conf | grep nameserver
echo ""

echo "Firewall status:"
if command -v ufw >/dev/null 2>&1; then
    ufw status 2>/dev/null | head -3 || echo "UFW недоступен"
else
    echo "UFW не установлен"
fi
echo ""

echo "==============================================="
echo "🔍 Сверхглубокий анализ завершен"