#!/bin/bash

# Останавливаем nginx
echo "Останавливаем nginx..."
sudo systemctl stop nginx

# Удаляем проблемные SSL конфиги
echo "Чистим SSL конфигурацию..."
sudo rm -rf /etc/letsencrypt/live/fan-club.kz 2>/dev/null || true
sudo rm -rf /etc/letsencrypt/archive/fan-club.kz 2>/dev/null || true
sudo rm -rf /etc/letsencrypt/renewal/fan-club.kz.conf 2>/dev/null || true

# Устанавливаем certbot если нет
echo "Проверяем certbot..."
if ! command -v certbot &> /dev/null; then
    echo "Устанавливаем certbot..."
    sudo apt update
    sudo apt install -y certbot
fi

# Получаем новый сертификат
echo "Получаем SSL сертификат для fan-club.kz..."
sudo certbot certonly --standalone -d fan-club.kz -d www.fan-club.kz --non-interactive --agree-tos --email admin@fan-club.kz

# Создаем конфигурацию nginx
echo "Создаем nginx конфигурацию..."
sudo tee /etc/nginx/sites-available/fan-club << 'EOF'
# HTTP redirect to HTTPS
server {
    listen 80;
    server_name fan-club.kz www.fan-club.kz;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name fan-club.kz www.fan-club.kz;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/fan-club.kz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/fan-club.kz/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }

    # Static files
    location /static/ {
        alias /var/www/myapp/eventsite/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Access-Control-Allow-Origin "*";
    }

    # Media files
    location /media/ {
        alias /var/www/myapp/eventsite/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Security - deny access to sensitive files
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
}

# Redirect www to non-www (optional)
server {
    listen 80;
    server_name www.fan-club.kz;
    return 301 https://fan-club.kz$request_uri;
}

server {
    listen 443 ssl http2;
    server_name www.fan-club.kz;

    ssl_certificate /etc/letsencrypt/live/fan-club.kz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/fan-club.kz/privkey.pem;

    return 301 https://fan-club.kz$request_uri;
}
