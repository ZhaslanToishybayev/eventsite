#!/bin/bash

# Complete UnitySphere Setup for fan-club.kz Domain
# Этот скрипт настраивает сайт для работы по доменному имени

echo "🌐 UnitySphere Complete Domain Setup for fan-club.kz"
echo "=================================================="

cd /var/www/myapp/eventsite

# 1. Запустить Django сервер
echo "🚀 Запускаем Django сервер..."
source venv/bin/activate

# Остановить предыдущие процессы
pkill -f "python.*manage.py.*runserver" 2>/dev/null || true
sleep 2

# Запустить сервер на 127.0.0.1:8000 (для Nginx reverse proxy)
python manage.py runserver 127.0.0.1:8000 &
DJANGO_PID=$!

echo "✅ Django сервер запущен (PID: $DJANGO_PID)"

# 2. Настроить Nginx
echo "🔧 Настраиваем Nginx..."

# Создать конфигурацию Nginx
sudo tee /etc/nginx/sites-available/fan-club.kz > /dev/null <<'EOF'
server {
    listen 80;
    server_name fan-club.kz www.fan-club.kz;

    # Redirect all HTTP to HTTPS (временно отключено)
    # return 301 https://$server_name$request_uri;

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
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
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

    # SSL Configuration (временно заглушка)
    ssl_certificate /etc/letsencrypt/live/fan-club.kz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/fan-club.kz/privkey.pem;

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
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
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

# Активировать сайт
sudo ln -sf /etc/nginx/sites-available/fan-club.kz /etc/nginx/sites-enabled/

# Проверить конфигурацию
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Конфигурация Nginx валидна"
    sudo systemctl reload nginx
    echo "✅ Nginx перезагружен"
else
    echo "❌ Ошибки в конфигурации Nginx"
    kill $DJANGO_PID
    exit 1
fi

# 3. Проверить доступность
echo "🔍 Проверяем доступность..."

sleep 3

# Проверить через curl (если установлен)
if command -v curl &> /dev/null; then
    echo "Проверка через curl..."
    curl -I http://fan-club.kz 2>/dev/null || echo "⚠️ fan-club.kz недоступен (проверьте DNS)"
    curl -I http://77.243.80.110 2>/dev/null || echo "⚠️ IP недоступен"
else
    echo "⚠️ curl не установлен, пропускаем проверку"
fi

# 4. Создать systemd сервис
echo "⚙️ Создаем systemd сервис..."
sudo tee /etc/systemd/system/unitysphere.service > /dev/null <<EOF
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
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=3
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
echo "✅ Systemd сервис создан"

# Финальный статус
echo ""
echo "🎉 UnitySphere Domain Setup Complete!"
echo "===================================="
echo ""
echo "🌐 Сайт теперь доступен по:"
echo "   - http://fan-club.kz"
echo "   - http://www.fan-club.kz"
echo "   - http://77.243.80.110"
echo "   - https://fan-club.kz (после SSL)"
echo ""
echo "✅ Что настроено:"
echo "   - Django сервер на 127.0.0.1:8000"
echo "   - Nginx reverse proxy"
echo "   - Static и media файлы"
echo "   - Security headers"
echo "   - Gzip compression"
echo "   - Systemd сервис"
echo ""
echo "📋 Следующие шаги:"
echo "   1. Проверьте DNS записи fan-club.kz → 77.243.80.110"
echo "   2. Установите SSL сертификаты: sudo certbot --nginx -d fan-club.kz"
echo "   3. Включите автозапуск: sudo systemctl enable unitysphere"
echo ""
echo "🛠️ Управление:"
echo "   - Остановить: kill $DJANGO_PID"
echo "   - Автозапуск: sudo systemctl enable unitysphere"
echo "   - Статус: sudo systemctl status unitysphere"
echo ""
echo "Нажмите Ctrl+C для остановки Django сервера"
echo ""

# Ждем, пока пользователь не прервет
wait $DJANGO_PID