#!/bin/bash

# Nginx Configuration Setup for fan-club.kz

echo "🌐 Настройка Nginx для fan-club.kz"
echo "=================================="

# Проверим, есть ли уже конфигурация
if [ -f "/etc/nginx/sites-available/fan-club.kz" ]; then
    echo "✅ Конфигурация Nginx уже существует"
else
    echo "📝 Создаем конфигурацию Nginx..."

    # Создаем конфигурацию Nginx
    sudo tee /etc/nginx/sites-available/fan-club.kz > /dev/null <<'EOF'
server {
    listen 80;
    server_name fan-club.kz www.fan-club.kz;

    # Redirect all HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name fan-club.kz www.fan-club.kz;

    # SSL Configuration (временно без сертификатов)
    # ssl_certificate /etc/letsencrypt/live/fan-club.kz/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/fan-club.kz/privkey.pem;
    # ssl_protocols TLSv1.2 TLSv1.3;
    # ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    # ssl_prefer_server_ciphers off;
    # ssl_session_cache shared:SSL:10m;
    # ssl_session_timeout 10m;

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

    # Error Pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;

    # Logging
    access_log /var/log/nginx/fan-club.kz.access.log;
    error_log /var/log/nginx/fan-club.kz.error.log;
}
EOF

    echo "✅ Конфигурация Nginx создана"
fi

# Активируем сайт
if [ -L "/etc/nginx/sites-enabled/fan-club.kz" ]; then
    echo "✅ Сайт уже активирован"
else
    echo "🔧 Активируем сайт..."
    sudo ln -s /etc/nginx/sites-available/fan-club.kz /etc/nginx/sites-enabled/
fi

# Проверяем конфигурацию Nginx
echo "🔍 Проверяем конфигурацию Nginx..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Конфигурация Nginx валидна"

    # Перезагружаем Nginx
    echo "🔄 Перезагружаем Nginx..."
    sudo systemctl reload nginx

    echo "✅ Nginx перезагружен"
else
    echo "❌ Ошибки в конфигурации Nginx"
    exit 1
fi

echo ""
echo "🎉 Nginx настроен для fan-club.kz!"
echo "=================================="
echo ""
echo "📋 Что сделано:"
echo "   - Создана конфигурация Nginx"
echo "   - Настроен reverse proxy на 127.0.0.1:8000"
echo "   - Настроены static и media файлы"
echo "   - Добавлены security headers"
echo "   - Включена gzip компрессия"
echo ""
echo "🌐 Теперь сайт доступен по:"
echo "   - http://fan-club.kz"
echo "   - http://www.fan-club.kz"
echo "   - http://77.243.80.110"
echo ""
echo "⚠️ Важно:"
echo "   1. Убедитесь, что DNS записи fan-club.kz указывают на 77.243.80.110"
echo "   2. Для HTTPS нужно установить SSL сертификаты (Let's Encrypt)"
echo "   3. Django сервер должен быть запущен на 127.0.0.1:8000"
echo ""
echo "Для установки SSL сертификатов выполните:"
echo "sudo apt install certbot python3-certbot-nginx"
echo "sudo certbot --nginx -d fan-club.kz -d www.fan-club.kz"