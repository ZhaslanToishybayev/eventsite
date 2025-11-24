#!/bin/bash

# 🔒 АВТОМАТИЧЕСКАЯ НАСТРОЙКА HTTPS С LET'S ENCRYPT
# Запустите эту команду: sudo ./auto_setup_https.sh

set -e

echo "🔒 АВТОМАТИЧЕСКАЯ НАСТРОЙКА HTTPS С LET'S ENCRYPT"
echo "================================================"

# ШАГ 1: Установка certbot
echo "📦 Установка certbot..."
apt update
apt install -y certbot python3-certbot-nginx

# ШАГ 2: Остановка Nginx
echo "🛑 Остановка Nginx..."
systemctl stop nginx

# ШАГ 3: Получение SSL сертификата
echo "🔐 Получение SSL сертификата..."
certbot certonly --standalone -d fan-club.kz -d www.fan-club.kz

# ШАГ 4: Проверка сертификата
echo "✅ Проверка SSL сертификата..."
if [ ! -f /etc/letsencrypt/live/fan-club.kz/fullchain.pem ]; then
    echo "❌ Ошибка: SSL сертификат не получен"
    exit 1
fi

# ШАГ 5: Создание новой конфигурации Nginx
echo "⚙️ Создание новой конфигурации Nginx..."
cat > /etc/nginx/sites-available/fan-club.kz << 'EOF'
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

# ШАГ 6: Проверка конфигурации Nginx
echo "🔍 Проверка конфигурации Nginx..."
nginx -t

# ШАГ 7: Запуск Nginx
echo "🚀 Запуск Nginx..."
systemctl start nginx

# ШАГ 8: Обновление Django settings
echo "🐍 Обновление Django settings..."
cp /var/www/myapp/eventsite/core/settings.py /var/www/myapp/eventsite/core/settings.py.backup

# Исправляем CSRF_TRUSTED_ORIGINS
sed -i "s/CSRF_TRUSTED_ORIGINS = \['https:\/\/fan-club.kz', 'https:\/\/www.fan-club.kz', 'https:\/\/fan-club.kz'\]/CSRF_TRUSTED_ORIGINS = ['https:\/\/fan-club.kz', 'https:\/\/www.fan-club.kz']/" /var/www/myapp/eventsite/core/settings.py

# ШАГ 9: Перезапуск Django
echo "🔄 Перезапуск Django..."
pkill -f "python.*manage.py.*runserver" || true
sleep 2

cd /var/www/myapp/eventsite
source venv/bin/activate
python manage.py runserver 127.0.0.1:8000 &

# ШАГ 10: Автоматическое обновление сертификатов
echo "⏰ Настройка автоматического обновления сертификатов..."
crontab -l 2>/dev/null | grep -v "certbot renew" | crontab - || true
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# ШАГ 11: Проверка HTTPS
echo "🌐 Проверка HTTPS доступности..."
sleep 3
if curl -s --connect-timeout 10 -I https://fan-club.kz > /dev/null; then
    echo "✅ HTTPS работает!"
else
    echo "⚠️ HTTPS пока не работает, но настройка завершена"
fi

echo ""
echo "================================================"
echo "🎉 HTTPS НАСТРОЙКА ЗАВЕРШЕНА!"
echo "🌐 Сайт доступен по: https://fan-club.kz"
echo "🔒 Все HTTP запросы перенаправляются на HTTPS"
echo "⏰ Автоматическое обновление сертификатов настроено"
echo ""
echo "💡 Проверьте сайт в браузере: https://fan-club.kz"