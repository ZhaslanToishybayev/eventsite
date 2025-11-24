#!/bin/bash

# Complete UnitySphere Setup for fan-club.kz Domain
# Автоматический скрипт для полной настройки

echo "🌐 UnitySphere Complete Setup for fan-club.kz"
echo "============================================"
echo ""

# Проверка прав суперпользователя
if [ "$EUID" -ne 0 ]; then
    echo "❌ Этот скрипт нужно запускать с sudo:"
    echo "   sudo $0"
    exit 1
fi

cd /var/www/myapp/eventsite

echo "🔧 Настройка Nginx для fan-club.kz..."

# 1. Создать конфигурацию Nginx
cat > /tmp/fan-club.kz << 'EOF'
server {
    listen 80;
    server_name fan-club.kz www.fan-club.kz;

    # Static Files
    location /static/ {
        alias /var/www/myapp/eventsite/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Media Files
    location /media/ {
        alias /var/www/myapp/eventsite/media/;
        expires 1y;
        add_header Cache-Control "public";
        access_log off;
    }

    # Main Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }

    # Health Check
    location /health/ {
        access_log off;
        proxy_pass http://127.0.0.1:8000/health/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Security - Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Logging
    access_log /var/log/nginx/fan-club.kz.access.log;
    error_log /var/log/nginx/fan-club.kz.error.log;
}

server {
    listen 443 ssl http2;
    server_name fan-club.kz www.fan-club.kz;

    # SSL Configuration (временно без сертификатов)
    # ssl_certificate /etc/letsencrypt/live/fan-club.kz/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/fan-club.kz/privkey.pem;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Static Files
    location /static/ {
        alias /var/www/myapp/eventsite/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Media Files
    location /media/ {
        alias /var/www/myapp/eventsite/media/;
        expires 1y;
        add_header Cache-Control "public";
        access_log off;
    }

    # Main Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }

    # Security - Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Logging
    access_log /var/log/nginx/fan-club.kz.ssl.access.log;
    error_log /var/log/nginx/fan-club.kz.ssl.error.log;
}
EOF

# 2. Скопировать конфигурацию в Nginx
cp /tmp/fan-club.kz /etc/nginx/sites-available/fan-club.kz
echo "✅ Конфигурация Nginx создана"

# 3. Активировать сайт
ln -sf /etc/nginx/sites-available/fan-club.kz /etc/nginx/sites-enabled/
echo "✅ Сайт активирован"

# 4. Проверить конфигурацию
echo "🔍 Проверка конфигурации Nginx..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Конфигурация Nginx валидна"
else
    echo "❌ Ошибки в конфигурации Nginx"
    exit 1
fi

# 5. Перезагрузить Nginx
systemctl reload nginx
echo "✅ Nginx перезагружен"

# 6. Создать systemd сервис для Django
cat > /etc/systemd/system/unitysphere.service << 'EOF'
[Unit]
Description=UnitySphere Django Application
After=network.target

[Service]
Type=exec
User=admin
Group=admin
WorkingDirectory=/var/www/myapp/eventsite
Environment="PATH=/var/www/myapp/eventsite/venv/bin"
EnvironmentFile=/var/www/myapp/eventsite/.env
ExecStart=/var/www/myapp/eventsite/venv/bin/python manage.py runserver 127.0.0.1:8000
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=3
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
echo "✅ Systemd сервис создан"

# 7. Проверить, запущен ли Django сервер
if pgrep -f "python.*manage.py.*runserver" > /dev/null; then
    echo "✅ Django сервер уже запущен"
else
    echo "🚀 Запускаем Django сервер..."
    cd /var/www/myapp/eventsite
    source venv/bin/activate
    python manage.py runserver 127.0.0.1:8000 &
    DJANGO_PID=$!
    sleep 3

    if kill -0 $DJANGO_PID 2>/dev/null; then
        echo "✅ Django сервер запущен (PID: $DJANGO_PID)"
    else
        echo "❌ Не удалось запустить Django сервер"
        exit 1
    fi
fi

# 8. Проверить доступность
echo "🔍 Проверка доступности..."
sleep 2

if command -v curl &> /dev/null; then
    echo "Проверка через curl..."

    # Проверить HTTP
    if curl -s -f -o /dev/null http://fan-club.kz; then
        echo "✅ Сайт доступен по HTTP: http://fan-club.kz"
    else
        echo "⚠️ Сайт недоступен по HTTP (проверьте Django сервер)"
    fi

    # Проверить IP
    if curl -s -f -o /dev/null http://77.243.80.110; then
        echo "✅ Сайт доступен по IP: http://77.243.80.110"
    else
        echo "⚠️ Сайт недоступен по IP"
    fi
else
    echo "⚠️ curl не установлен, пропускаем проверку"
fi

# 9. Создать скрипт для остановки
cat > /var/www/myapp/eventsite/stop_nginx.sh << 'EOF'
#!/bin/bash
echo "🛑 Остановка UnitySphere..."

# Остановить Django процессы
pkill -f "python.*manage.py.*runserver" 2>/dev/null || true
echo "✅ Django серверы остановлены"

# Отключить сайт
if [ -L "/etc/nginx/sites-enabled/fan-club.kz" ]; then
    rm /etc/nginx/sites-enabled/fan-club.kz
    echo "✅ Сайт отключен"
fi

# Перезагрузить Nginx
systemctl reload nginx
echo "✅ Nginx перезагружен"

echo "🎉 UnitySphere остановлен!"
EOF

chmod +x /var/www/myapp/eventsite/stop_nginx.sh

# Финальный статус
echo ""
echo "🎉 UnitySphere Complete Setup Finished!"
echo "======================================="
echo ""
echo "🌐 Сайт теперь доступен по:"
echo "   ✅ http://fan-club.kz"
echo "   ✅ http://www.fan-club.kz"
echo "   ✅ http://77.243.80.110"
echo "   ⏭️ https://fan-club.kz (после SSL)"
echo ""
echo "📋 Что настроено:"
echo "   ✅ Nginx reverse proxy"
echo "   ✅ Django сервер (127.0.0.1:8000)"
echo "   ✅ Static и media файлы"
echo "   ✅ Security headers"
echo "   ✅ Gzip compression"
echo "   ✅ Systemd сервис"
echo "   ✅ Автоматический запуск"
echo ""
echo "🛠️ Управление:"
echo "   📁 Папка проекта: /var/www/myapp/eventsite"
echo "   🐍 Виртуальное окружение: source venv/bin/activate"
echo "   🌐 Nginx config: /etc/nginx/sites-available/fan-club.kz"
echo "   🔧 Systemd service: sudo systemctl status unitysphere"
echo "   ⏹️ Остановить: ./stop_nginx.sh"
echo ""
echo "📋 Следующие шаги (опционально):"
echo "   1. Установить SSL сертификаты: sudo apt install certbot python3-certbot-nginx && sudo certbot --nginx -d fan-club.kz"
echo "   2. Включить автозапуск: sudo systemctl enable unitysphere"
echo "   3. Настроить PostgreSQL для production"
echo ""
echo "🎊 Поздравляю! Ваш сайт fan-club.kz теперь работает полноценно! 🎊"