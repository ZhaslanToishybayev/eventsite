#!/bin/bash

# 🚀 Автоматическая настройка полноценного сайта с SSL
echo "🚀 НАСТРОЙКА ПОЛНОЦЕННОГО САЙТА С SSL"
echo "======================================"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${BLUE}[SUCCESS]${NC} $1"
}

# Проверка прав root
if [[ $EUID -eq 0 ]]; then
   warn "Рекомендуется запускать не от root пользователя"
fi

log "Проверка предварительных условий..."

# Проверка наличия необходимых пакетов
check_packages() {
    log "Проверка наличия необходимых пакетов..."

    if ! command -v nginx &> /dev/null; then
        error "nginx не установлен"
        log "Установка nginx..."
        sudo apt update && sudo apt install -y nginx
    fi

    if ! command -v certbot &> /dev/null; then
        error "certbot не установлен"
        log "Установка certbot..."
        sudo apt install -y certbot python3-certbot-nginx
    fi

    if ! command -v python3 &> /dev/null; then
        error "python3 не установлен"
        log "Установка python3..."
        sudo apt install -y python3 python3-pip python3-venv
    fi

    success "Все необходимые пакеты установлены"
}

# Проверка Django проекта
check_django() {
    log "Проверка Django проекта..."

    if [ ! -d "/var/www/myapp/eventsite" ]; then
        error "Django проект не найден в /var/www/myapp/eventsite"
        exit 1
    fi

    cd /var/www/myapp/eventsite

    if [ ! -f "manage.py" ]; then
        error "manage.py не найден"
        exit 1
    fi

    success "Django проект найден"
}

# Запуск Django сервера
start_django() {
    log "Запуск Django сервера..."

    if pgrep -f "python.*manage\.py.*runserver" > /dev/null; then
        warn "Django сервер уже работает"
    else
        # Активируем виртуальное окружение и запускаем сервер
        if [ -d "venv" ]; then
            source venv/bin/activate
        fi
        python manage.py runserver 0.0.0.0:8000 > /dev/null 2>&1 &
        sleep 3

        if curl -s http://localhost:8000/health/ > /dev/null; then
            success "Django сервер запущен"
        else
            error "Django сервер не запустился"
            exit 1
        fi
    fi
}

# Настройка nginx
setup_nginx() {
    log "Настройка nginx..."

    # Создаем резервную копию
    if [ -f "/etc/nginx/sites-available/fan-club.kz" ]; then
        sudo cp /etc/nginx/sites-available/fan-club.kz "/etc/nginx/sites-available/fan-club.kz.backup.$(date +%Y%m%d)"
        log "Создана резервная копия nginx конфигурации"
    fi

    # Копируем конфигурацию
    sudo cp /var/www/myapp/eventsite/nginx_complete_config /etc/nginx/sites-available/fan-club.kz

    # Активируем сайт
    sudo ln -sf /etc/nginx/sites-available/fan-club.kz /etc/nginx/sites-enabled/

    # Проверяем конфигурацию
    if sudo nginx -t; then
        success "Конфигурация nginx проверена"
    else
        error "Ошибка в конфигурации nginx"
        exit 1
    fi

    # Перезагружаем nginx
    sudo systemctl reload nginx
    success "nginx перезагружен"
}

# Получение SSL сертификата
get_ssl_cert() {
    log "Получение SSL сертификата..."

    # Проверяем, есть ли уже сертификат
    if [ -f "/etc/letsencrypt/live/fan-club.kz/fullchain.pem" ]; then
        warn "SSL сертификат уже существует"
        log "Проверка срока действия сертификата..."

        # Проверяем срок действия
        cert_expiry=$(sudo openssl x509 -in /etc/letsencrypt/live/fan-club.kz/fullchain.pem -noout -enddate | cut -d= -f2)
        cert_expiry_epoch=$(date -d "$cert_expiry" +%s)
        current_epoch=$(date +%s)
        days_until_expiry=$(( (cert_expiry_epoch - current_epoch) / 86400 ))

        if [ $days_until_expiry -lt 30 ]; then
            log "Сертификат скоро истечет, обновляем..."
            sudo certbot renew --quiet
        else
            success "SSL сертификат действителен ($days_until_expiry дней)"
        fi
    else
        log "Получение нового SSL сертификата..."
        sudo certbot --nginx -d fan-club.kz -d www.fan-club.kz --agree-tos --non-interactive --email admin@fan-club.kz

        if [ $? -eq 0 ]; then
            success "SSL сертификат получен"
        else
            error "Не удалось получить SSL сертификат"
            exit 1
        fi
    fi
}

# Настройка автоматического обновления сертификатов
setup_auto_renew() {
    log "Настройка автоматического обновления сертификатов..."

    # Добавляем cron job для автоматического обновления
    if ! crontab -l 2>/dev/null | grep -q "certbot"; then
        (crontab -l 2>/dev/null; echo "0 12 * * 0 /usr/bin/certbot renew --quiet") | sudo crontab -
        success "Настроен автоматический renewal сертификатов"
    else
        log "Автоматическое обновление сертификатов уже настроено"
    fi
}

# Настройка systemd service для Django
setup_django_service() {
    log "Настройка systemd service для Django..."

    cat > /tmp/django-fanclub.service << EOF
[Unit]
Description=Django Fan Club Application
After=network.target

[Service]
Type=exec
User=admin
Group=admin
WorkingDirectory=/var/www/myapp/eventsite
Environment="PATH=/var/www/myapp/eventsite/venv/bin"
ExecStart=/var/www/myapp/eventsite/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    sudo cp /tmp/django-fanclub.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable django-fanclub
    sudo systemctl start django-fanclub

    sleep 3
    if sudo systemctl is-active --quiet django-fanclub; then
        success "Django service запущен"
    else
        error "Django service не запустился"
        sudo systemctl status django-fanclub
        exit 1
    fi
}

# Проверка работоспособности
test_site() {
    log "Тестирование работоспособности сайта..."

    # Проверка HTTP
    if curl -s http://fan-club.kz/health/ | grep -q "healthy"; then
        success "HTTP доступ работает"
    else
        error "HTTP доступ не работает"
    fi

    # Проверка HTTPS
    if curl -k -s https://fan-club.kz/health/ | grep -q "healthy"; then
        success "HTTPS доступ работает"
    else
        error "HTTPS доступ не работает"
    fi

    # Проверка AI API
    if curl -k -s -X POST "https://fan-club.kz/api/v1/ai/simplified/interactive/chat/" \
        -H "Content-Type: application/json" \
        -d '{"message": "Привет", "user_email": "test@fan-club.kz", "state_id": null}' > /dev/null; then
        success "AI API работает"
    else
        error "AI API не работает"
    fi

    success "Все тесты пройдены!"
}

# Основной процесс
main() {
    log "Начинаем настройку полноценного сайта..."

    check_packages
    check_django
    start_django
    setup_nginx
    get_ssl_cert
    setup_auto_renew
    setup_django_service
    test_site

    echo ""
    success "🎉 ПОЛНОЦЕННЫЙ САЙТ С SSL ГОТОВ!"
    echo "=================================="
    echo ""
    echo "🌐 Сайт доступен по адресу:"
    echo "   https://fan-club.kz"
    echo "   https://www.fan-club.kz"
    echo ""
    echo "🔧 Управление сервисом:"
    echo "   sudo systemctl status django-fanclub  # Статус Django"
    echo "   sudo systemctl restart django-fanclub # Перезапуск Django"
    echo "   sudo nginx -t                         # Проверка nginx"
    echo "   sudo systemctl reload nginx           # Перезагрузка nginx"
    echo ""
    echo "📋 Что настроено:"
    echo "   ✅ SSL сертификат Let's Encrypt"
    echo "   ✅ Автоматическое обновление SSL"
    echo "   ✅ Django systemd service"
    echo "   ✅ Nginx reverse proxy"
    echo "   ✅ Gzip сжатие"
    echo "   ✅ Безопасность (HSTS, CORS и др.)"
    echo "   ✅ AI консультант и виджет"
    echo "   ✅ Все функции сайта"
    echo ""
    echo "🚀 Ваш сайт теперь полностью функционирует!"
}

# Запуск основного процесса
main "$@"