#!/bin/bash

# ПОЛНАЯ НАСТРОЙКА HTTPS С LET'S ENCRYPT
echo "🔒 ПОЛНАЯ НАСТРОЙКА HTTPS С LET'S ENCRYPT"
echo "============================================"

echo "1. Установка certbot..."
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

echo ""
echo "2. Остановка Nginx для получения сертификата..."
sudo systemctl stop nginx

echo ""
echo "3. Получение SSL сертификата..."
sudo certbot certonly --standalone -d fan-club.kz -d www.fan-club.kz

echo ""
echo "4. Проверка получения сертификата..."
if [ -f /etc/letsencrypt/live/fan-club.kz/fullchain.pem ]; then
    echo "✅ SSL сертификат получен!"
    echo "Сертификат: /etc/letsencrypt/live/fan-club.kz/fullchain.pem"
    echo "Приватный ключ: /etc/letsencrypt/live/fan-club.kz/privkey.pem"
else
    echo "❌ Ошибка получения сертификата"
    exit 1
fi

echo ""
echo "5. Создание новой конфигурации Nginx с HTTPS..."
sudo cp /etc/nginx/sites-available/fan-club.kz /etc/nginx/sites-available/fan-club.kz.backup

sudo cat > /etc/nginx/sites-available/fan-club.kz << 'EOF'
# HTTP редирект на HTTPS
server {
    listen 80;
    server_name fan-club.kz www.fan-club.kz;
    return 301 https://$server_name$request_uri;
}

# HTTPS сервер
server {
    listen 443 ssl http2;
    server_name fan-club.kz www.fan-club.kz;

    ssl_certificate /etc/letsencrypt/live/fan-club.kz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/fan-club.kz/privkey.pem;

    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

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
        proxy_set_header X-Forwarded-Host $host;
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

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
        allow all;
    }

    # Logging
    access_log /var/log/nginx/fan-club.kz.access.log;
    error_log /var/log/nginx/fan-club.kz.error.log;
}
EOF

echo ""
echo "6. Проверка конфигурации Nginx..."
sudo nginx -t

echo ""
echo "7. Обновление Django settings для HTTPS..."
# Создадим резервную копию
cp /var/www/myapp/eventsite/core/settings.py /var/www/myapp/eventsite/core/settings.py.backup

# Обновим CSRF_TRUSTED_ORIGINS для HTTPS
sed -i "s/CSRF_TRUSTED_ORIGINS = \['https:\/\/fan-club.kz', 'https:\/\/www.fan-club.kz', 'https:\/\/fan-club.kz'\]/CSRF_TRUSTED_ORIGINS = ['https:\/\/fan-club.kz', 'https:\/\/www.fan-club.kz']/" /var/www/myapp/eventsite/core/settings.py

echo ""
echo "8. Запуск Nginx..."
sudo systemctl start nginx

echo ""
echo "9. Проверка статуса Nginx..."
sudo systemctl status nginx --no-pager -l

echo ""
echo "10. Автоматическое обновление сертификатов..."
sudo crontab -l | grep -q "certbot" || (sudo crontab -l; echo "0 12 * * * /usr/bin/certbot renew --quiet") | sudo crontab -

echo ""
echo "11. Проверка HTTPS доступности..."
echo "Проверяем HTTPS соединение..."
curl -I --connect-timeout 10 https://fan-club.kz

echo ""
echo "============================================"
echo "✅ HTTPS настройка завершена!"
echo "🌐 Сайт доступен по: https://fan-club.kz"
echo "🔐 Автоматическое обновление сертификатов настроено"
echo "📝 Django settings обновлены для HTTPS"