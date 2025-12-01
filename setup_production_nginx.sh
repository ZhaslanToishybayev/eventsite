#!/bin/bash

# 🚀 Production nginx Setup Script for UnitySphere
# Идеальная настройка nginx для финального запуска сайта

echo "🚀 НАСТРОЙКА PRODUCTION NGINX ДЛЯ UNITYSPHERE"
echo "=============================================="

# Проверяем запущен ли Django
echo "🔍 Проверяем Django сервер..."
if curl -s http://127.0.0.1:8080/ > /dev/null; then
    echo "✅ Django работает на порту 8080"
else
    echo "❌ Django не работает на порту 8080"
    echo "Запускаем Django..."
    cd /var/www/myapp/eventsite
    source venv/bin/activate
    python manage.py runserver 0.0.0.0:8080 --insecure &
    sleep 5
fi

# Создаем резервную копию текущей конфигурации nginx
echo "📦 Создаем резервную копию текущей конфигурации nginx..."
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup 2>/dev/null || echo "⚠️  Не удалось создать резервную копию (возможно нет доступа sudo)"

# Создаем оптимальную конфигурацию nginx
echo "⚙️  Создаем оптимальную конфигурацию nginx..."
cat > /tmp/nginx_production.conf << 'EOF'
# 🚀 UnitySphere Production Configuration - IDEAL SETUP
# Адаптивный, быстрый, безопасный nginx + Django

# Основной сервер для fan-club.kz
server {
    listen 80;
    listen [::]:80;
    server_name fan-club.kz www.fan-club.kz;

    # 🛡️ Безопасность
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # 📁 Статические файлы (максимальная производительность)
    location /static/ {
        alias /var/www/myapp/eventsite/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;

        # Оптимизация для разных типов файлов
        location ~* \.(css|js)$ {
            expires 1M;
            add_header Cache-Control "public";
        }

        location ~* \.(jpg|jpeg|png|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # 📂 Медиа файлы
    location /media/ {
        alias /var/www/myapp/eventsite/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # 🤖 AI Widget API (высокий приоритет)
    location /api/v1/ai/production/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Таймауты для AI
        proxy_connect_timeout 30s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # CORS для виджета
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept, Authorization" always;
    }

    # 🐛 Health check
    location /health/ {
        proxy_pass http://127.0.0.1:8080;
        access_log off;
    }

    # 🌐 Все остальные запросы → Django
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Оптимизация проксирования
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;

        # Таймауты
        proxy_connect_timeout 30s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 🚫 Запрет доступа к служебным файлам
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # 📊 Статистика (если нужно)
    location /nginx_status {
        stub_status on;
        allow 127.0.0.1;
        deny all;
    }
}

# 🔒 HTTPS редирект (если будет SSL)
# server {
#     listen 443 ssl http2;
#     server_name fan-club.kz www.fan-club.kz;
#
#     ssl_certificate /path/to/certificate.crt;
#     ssl_certificate_key /path/to/private.key;
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
#
#     # Весь трафик идет на Django
#     location / {
#         proxy_pass http://127.0.0.1:8080;
#         # ... остальные настройки проксирования
#     }
# }

# 🔄 HTTP → HTTPS редирект
# server {
#     listen 80;
#     server_name fan-club.kz www.fan-club.kz;
#     return 301 https://$server_name$request_uri;
# }
EOF

# Копируем конфигурацию в nginx (если есть доступ)
echo "📋 Копируем конфигурацию в nginx..."
if sudo cp /tmp/nginx_production.conf /etc/nginx/nginx.conf 2>/dev/null; then
    echo "✅ Конфигурация nginx скопирована"
else
    echo "⚠️  Нет доступа sudo. Конфигурация сохранена в /tmp/nginx_production.conf"
    echo "   Вам нужно вручную скопировать её в /etc/nginx/nginx.conf"
    echo "   Или выполнить: sudo cp /tmp/nginx_production.conf /etc/nginx/nginx.conf"
fi

# Проверяем конфигурацию nginx
echo "🔍 Проверяем конфигурацию nginx..."
if sudo nginx -t 2>/dev/null; then
    echo "✅ Конфигурация nginx валидна"
else
    echo "⚠️  Проблемы с конфигурацией nginx"
    echo "   Проверьте файл /tmp/nginx_production.conf"
fi

# Перезапускаем nginx (если есть доступ)
echo "🔄 Перезапускаем nginx..."
if sudo systemctl restart nginx 2>/dev/null; then
    echo "✅ Nginx перезапущен"
elif sudo service nginx restart 2>/dev/null; then
    echo "✅ Nginx перезапущен"
else
    echo "⚠️  Нет доступа для перезапуска nginx"
    echo "   Выполните вручную: sudo systemctl restart nginx"
fi

# Проверяем доступность сайта
echo "🌐 Проверяем доступность сайта..."
sleep 3
if curl -s http://fan-club.kz/ > /dev/null; then
    echo "✅ Сайт доступен по fan-club.kz"
elif curl -s http://127.0.0.1/ > /dev/null; then
    echo "✅ Сайт доступен по localhost"
else
    echo "❌ Сайт недоступен"
fi

# Информация для пользователя
echo ""
echo "🎯 ИНФОРМАЦИЯ ПО ЗАПУСКУ:"
echo "=========================="
echo "🌐 Сайт должен быть доступен по:"
echo "   - http://fan-club.kz/"
echo "   - http://www.fan-club.kz/"
echo "   - http://77.243.80.110/"
echo ""
echo "🤖 AI Widget должен работать по адресу:"
echo "   - /api/v1/ai/production/agent/"
echo ""
echo "🛠️  Если nginx не перезапустился:"
echo "   1. Скопируйте конфигурацию: sudo cp /tmp/nginx_production.conf /etc/nginx/nginx.conf"
echo "   2. Перезапустите nginx: sudo systemctl restart nginx"
echo "   3. Проверьте статус: sudo systemctl status nginx"
echo ""
echo "📋 Текущий статус сервисов:"
echo "   Django: $(curl -s http://127.0.0.1:8080/ > /dev/null && echo '✅ Работает' || echo '❌ Не работает')"
if command -v nginx >/dev/null 2>&1; then
    echo "   Nginx: $(pgrep nginx > /dev/null && echo '✅ Работает' || echo '❌ Не работает')"
fi
echo ""
echo "🎉 Готово! Сайт должен работать с AI виджетом!"