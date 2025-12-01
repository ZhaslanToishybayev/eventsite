#!/bin/bash

# 🚀 Quick Fix Script for UnitySphere Production
# Быстрое исправление и запуск системы на production

echo "🚀 Quick Fix UnitySphere Production"
echo "==================================="
echo ""

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Проверка прав суперпользователя
if [ "$EUID" -ne 0 ]; then
    print_error "Требуются права суперпользователя. Запустите: sudo $0"
    exit 1
fi

print_info "Начинаем быстрое исправление UnitySphere..."

# 1. Проверка и настройка Django
print_info "1. Проверка Django конфигурации..."
cd /var/www/myapp/eventsite

# Проверка и исправление ALLOWED_HOSTS
if grep -q "'fan-club.kz'" core/settings.py; then
    print_success "ALLOWED_HOSTS уже настроен"
else
    # Найдем и заменим ALLOWED_HOSTS
    sed -i "s/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = ['fan-club.kz', 'www.fan-club.kz', '127.0.0.1', 'localhost', '0.0.0.0']/" core/settings.py
    if grep -q "'fan-club.kz'" core/settings.py; then
        print_success "ALLOWED_HOSTS настроен для production"
    else
        print_error "Не удалось настроить ALLOWED_HOSTS"
        exit 1
    fi
fi

# 2. Проверка Django сервера
print_info "2. Проверка Django сервера..."
if curl -s http://127.0.0.1:8001/ > /dev/null; then
    print_success "Django сервер работает"
else
    print_warning "Django сервер не отвечает, перезапускаем..."
    # Остановим все Django процессы
    pkill -f "manage.py runserver" || true
    sleep 2

    # Запустим Django сервер
    source venv/bin/activate
    nohup python manage.py runserver 127.0.0.1:8001 --insecure > /tmp/django.log 2>&1 &
    sleep 5

    if curl -s http://127.0.0.1:8001/ > /dev/null; then
        print_success "Django сервер запущен"
    else
        print_error "Django сервер не запустился"
        print_info "Проверка логов: tail -f /tmp/django.log"
        exit 1
    fi
fi

# 3. Проверка и настройка nginx
print_info "3. Проверка nginx конфигурации..."

# Проверка SSL сертификата
if [ -f "/etc/letsencrypt/live/fan-club.kz/fullchain.pem" ]; then
    print_success "SSL сертификат найден"
else
    print_warning "SSL сертификат не найден, используем HTTP"
fi

# Создание простой nginx конфигурации
cat > /etc/nginx/sites-available/unitysphere << 'EOF'
server {
    listen 80;
    server_name fan-club.kz www.fan-club.kz;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/unitysphere_access.log;
    error_log /var/log/nginx/unitysphere_error.log;

    # Health check
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Static files
    location /static/ {
        alias /var/www/myapp/eventsite/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/myapp/eventsite/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Main application
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Активация сайта
ln -sf /etc/nginx/sites-available/unitysphere /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Проверка конфигурации
if nginx -t 2>/dev/null; then
    print_success "Конфигурация nginx валидна"
else
    print_error "Ошибка в конфигурации nginx"
    exit 1
fi

# 4. Перезапуск nginx
print_info "4. Перезапуск nginx..."
systemctl restart nginx
if systemctl is-active --quiet nginx; then
    print_success "nginx перезапущен"
else
    print_error "nginx не запустился"
    exit 1
fi

# 5. Тестирование системы
print_info "5. Тестирование системы..."
sleep 3

# Проверка через nginx
response=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/ || echo "000")
if [ "$response" = "200" ]; then
    print_success "Сайт доступен через nginx (HTTP $response)"
else
    print_error "Сайт недоступен (HTTP $response)"
    print_info "Проверка напрямую к Django..."
    direct_response=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/ || echo "000")
    if [ "$direct_response" = "200" ]; then
        print_warning "Django работает, проблема в nginx"
    else
        print_error "Проблема с Django"
    fi
    exit 1
fi

# Проверка AI API
api_response=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/api/v1/ai/health/ || echo "000")
if [ "$api_response" = "200" ]; then
    print_success "AI API доступен"
else
    print_warning "AI API недоступен (HTTP $api_response)"
fi

# 6. Открытие портов
print_info "6. Настройка firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp 2>/dev/null || true
    ufw allow 443/tcp 2>/dev/null || true
    print_success "Firewall настроен"
else
    print_warning "ufw not found, please configure firewall manually"
fi

# Финальная информация
echo ""
echo "🎉 UnitySphere Quick Fix Completed!"
echo "==================================="
echo ""
echo "🔗 Сайт доступен:"
echo "   http://fan-club.kz"
echo ""
echo "⚙️ Команды для управления:"
echo "   # Проверить статус nginx"
echo "   systemctl status nginx"
echo ""
echo "   # Проверить Django процесс"
echo "   ps aux | grep runserver"
echo ""
echo "   # Проверить логи Django"
echo "   tail -f /tmp/django.log"
echo ""
echo "   # Перезапустить nginx"
echo "   systemctl restart nginx"
echo ""
echo "✅ Production system is now working!"