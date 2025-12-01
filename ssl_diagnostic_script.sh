#!/bin/bash

# 🔍 SSL Diagnostic Script for fan-club.kz
# Скрипт диагностики SSL сертификатов и автоматического исправления

echo "🔍 Запуск диагностики SSL сертификатов для fan-club.kz..."
echo "================================================================"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для печати разделителей
print_separator() {
    echo "----------------------------------------------------------------"
}

# Функция для успешного сообщения
success_msg() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Функция для ошибки
error_msg() {
    echo -e "${RED}❌ $1${NC}"
}

# Функция для предупреждения
warning_msg() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Функция для информации
info_msg() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Проверка статуса nginx
check_nginx_status() {
    print_separator
    echo "📋 Проверка статуса nginx..."

    if systemctl is-active --quiet nginx; then
        success_msg "nginx работает"
        nginx_status="running"
    else
        error_msg "nginx не работает"
        nginx_status="stopped"
    fi

    # Проверка конфигурации nginx
    echo "📋 Проверка конфигурации nginx..."
    if nginx -t 2>&1 | grep -q "syntax is ok"; then
        success_msg "Синтаксис nginx конфигурации корректен"
        nginx_config_ok=true
    else
        error_msg "Синтаксис nginx конфигурации содержит ошибки"
        nginx_config_ok=false
        nginx -t
    fi
}

# Проверка SSL сертификатов
check_ssl_certificates() {
    print_separator
    echo "🔒 Проверка SSL сертификатов..."

    cert_path="/etc/letsencrypt/live/fan-club.kz"
    fullchain_cert="$cert_path/fullchain.pem"
    privkey_cert="$cert_path/privkey.pem"

    # Проверка существования файлов сертификатов
    if [[ -f "$fullchain_cert" ]]; then
        success_msg "Найден SSL сертификат: $fullchain_cert"
        fullchain_exists=true
    else
        error_msg "SSL сертификат не найден: $fullchain_cert"
        fullchain_exists=false
    fi

    if [[ -f "$privkey_cert" ]]; then
        success_msg "Найден SSL приватный ключ: $privkey_cert"
        privkey_exists=true
    else
        error_msg "SSL приватный ключ не найден: $privkey_cert"
        privkey_exists=false
    fi

    # Проверка валидности сертификатов
    if [[ $fullchain_exists == true ]]; then
        echo "📋 Проверка срока действия сертификата..."
        cert_expiry=$(openssl x509 -enddate -noout -in "$fullchain_cert" 2>/dev/null | cut -d= -f2)
        if [[ $? -eq 0 ]]; then
            expiry_date=$(date -d "$cert_expiry" '+%d.%m.%Y %H:%M:%S')
            current_date=$(date '+%d.%m.%Y %H:%M:%S')

            if [[ $(date -d "$cert_expiry" +%s) -gt $(date +%s) ]]; then
                success_msg "Сертификат действителен до: $expiry_date"
                cert_valid=true
            else
                error_msg "Сертификат просрочен! Срок действия: $expiry_date"
                cert_valid=false
            fi
        else
            error_msg "Не удалось проверить срок действия сертификата"
            cert_valid=false
        fi
    fi

    # Проверка конфигурации nginx на использование SSL
    echo "📋 Проверка nginx конфигурации на SSL..."
    nginx_config="/etc/nginx/sites-enabled/fan-club.kz"
    if [[ -f "$nginx_config" ]] && grep -q "ssl_certificate" "$nginx_config"; then
        info_msg "Nginx конфигурация использует SSL сертификаты"
        nginx_uses_ssl=true
    else
        info_msg "Nginx конфигурация не использует SSL"
        nginx_uses_ssl=false
    fi
}

# Проверка доступности сайта
check_website_access() {
    print_separator
    echo "🌐 Проверка доступности сайта..."

    # Проверка локального Django сервера
    echo "📋 Проверка Django сервера на localhost:8000..."
    if curl -s --connect-timeout 5 http://localhost:8000 > /dev/null; then
        success_msg "Django сервер доступен на localhost:8000"
        django_ok=true
    else
        error_msg "Django сервер недоступен на localhost:8000"
        django_ok=false
    fi

    # Проверка AI API
    echo "📋 Проверка AI API..."
    if curl -s --connect-timeout 5 http://localhost:8000/api/v1/ai/simplified/interactive/status/ > /dev/null; then
        success_msg "AI API доступен"
        ai_api_ok=true
    else
        error_msg "AI API недоступен"
        ai_api_ok=false
    fi

    # Проверка через nginx (если работает)
    if [[ $nginx_status == "running" ]]; then
        echo "📋 Проверка сайта через nginx..."
        if curl -s --connect-timeout 5 http://fan-club.kz > /dev/null; then
            success_msg "Сайт доступен через nginx (HTTP)"
            nginx_http_ok=true
        else
            error_msg "Сайт недоступен через nginx (HTTP)"
            nginx_http_ok=false
        fi

        # Проверка HTTPS
        if curl -s --connect-timeout 5 https://fan-club.kz > /dev/null; then
            success_msg "Сайт доступен через nginx (HTTPS)"
            nginx_https_ok=true
        else
            error_msg "Сайт недоступен через nginx (HTTPS)"
            nginx_https_ok=false
        fi
    fi
}

# Анализ проблемы
analyze_problem() {
    print_separator
    echo "🔍 Анализ проблем..."

    issues=()
    solutions=()

    if [[ $nginx_status != "running" ]]; then
        issues+=("nginx не запущен")
        solutions+=("systemctl start nginx")
    fi

    if [[ $nginx_config_ok == false ]]; then
        issues+=("ошибки в конфигурации nginx")
        solutions+=("исправить конфигурацию nginx")
    fi

    if [[ $django_ok == false ]]; then
        issues+=("Django сервер не работает")
        solutions+=("запустить Django: source venv/bin/activate && python manage.py runserver 0.0.0.0:8000")
    fi

    if [[ $ai_api_ok == false ]]; then
        issues+=("AI API не работает")
        solutions+=("проверить Django сервер и AI модули")
    fi

    if [[ $nginx_uses_ssl == true ]] && ([[ $fullchain_exists == false ]] || [[ $privkey_exists == false ]] || [[ $cert_valid == false ]]); then
        issues+=("SSL сертификаты отсутствуют или недействительны")
        solutions+=("ssl_fix")
    fi

    if [[ $nginx_https_ok == false ]] && [[ $django_ok == true ]] && [[ $nginx_status == "running" ]]; then
        issues+=("HTTPS недоступен, но бэкенд работает")
        solutions+=("ssl_fix")
    fi

    # Вывод проблем
    if [[ ${#issues[@]} -eq 0 ]]; then
        success_msg "Проблем не обнаружено! Сайт должен работать нормально."
    else
        echo ""
        error_msg "Обнаруженные проблемы:"
        for issue in "${issues[@]}"; do
            echo "  - $issue"
        done

        echo ""
        warning_msg "Предлагаемые решения:"
        for solution in "${solutions[@]}"; do
            if [[ $solution == "ssl_fix" ]]; then
                echo "  - Выполнить SSL фикс (автоматически)"
            else
                echo "  - $solution"
            fi
        done
    fi
}

# Автоматическое исправление SSL проблем
fix_ssl_problems() {
    print_separator
    echo "🔧 Автоматическое исправление SSL проблем..."

    read -p "Вы хотите выполнить автоматическое исправление? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info_msg "Автоматическое исправление отменено"
        return
    fi

    # Создание резервной копии текущей конфигурации
    backup_dir="/etc/nginx/backup_$(date +%Y%m%d_%H%M%S)"
    echo "📋 Создание резервной копии конфигурации..."
    sudo mkdir -p "$backup_dir"
    sudo cp /etc/nginx/sites-available/fan-club.kz "$backup_dir/" 2>/dev/null || true
    sudo cp /etc/nginx/sites-enabled/fan-club.kz "$backup_dir/" 2>/dev/null || true
    success_msg "Резервная копия создана: $backup_dir"

    # Вариант 1: Простая HTTP конфигурация (без SSL)
    echo ""
    echo "Выберите вариант исправления:"
    echo "1. Простая HTTP конфигурация (без SSL) - быстрое решение"
    echo "2. Полная SSL настройка с Let's Encrypt"
    echo "3. Отмена"

    read -p "Введите выбор (1-3): " -n 1 -r
    echo

    case $REPLY in
        1)
            fix_with_http
            ;;
        2)
            fix_with_ssl
            ;;
        3)
            info_msg "Исправление отменено"
            ;;
        *)
            error_msg "Неверный выбор"
            ;;
    esac
}

# Исправление с HTTP конфигурацией
fix_with_http() {
    echo "🔧 Установка HTTP конфигурации..."

    # Копируем простую конфигурацию
    if [[ -f "/var/www/myapp/eventsite/nginx_simple_config" ]]; then
        sudo cp /var/www/myapp/eventsite/nginx_simple_config /etc/nginx/sites-available/fan-club
        success_msg "Скопирована простая HTTP конфигурация"
    else
        error_msg "Файл простой конфигурации не найден, создаем вручную..."

        # Создаем простую конфигурацию вручную
        sudo tee /etc/nginx/sites-available/fan-club > /dev/null << 'EOF'
# Простая конфигурация nginx без SSL
server {
    listen 80;
    server_name fan-club.kz www.fan-club.kz;

    # Основное приложение
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Статические файлы
    location /static/ {
        alias /var/www/myapp/eventsite/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Медиа файлы
    location /media/ {
        alias /var/www/myapp/eventsite/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Проверка работоспособности
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Безопасность - запрет доступа к скрытым файлам
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}

# Редирект с www на основной домен
server {
    listen 80;
    server_name www.fan-club.kz;
    return 301 http://fan-club.kz$request_uri;
}
EOF
        success_msg "Создана простая HTTP конфигурация"
    fi

    # Активируем новую конфигурацию
    sudo ln -sf /etc/nginx/sites-available/fan-club /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/fan-club.kz

    # Проверяем конфигурацию
    if nginx -t; then
        success_msg "Конфигурация nginx проверена"
        # Перезапускаем nginx
        sudo systemctl restart nginx
        if systemctl is-active --quiet nginx; then
            success_msg "nginx перезапущен"
            echo ""
            success_msg "✅ HTTP конфигурация установлена! Сайт должен быть доступен по http://fan-club.kz"
        else
            error_msg "nginx не запустился после перезагрузки"
        fi
    else
        error_msg "Ошибка в конфигурации nginx"
    fi
}

# Исправление с SSL
fix_with_ssl() {
    echo "🔧 Настройка SSL с Let's Encrypt..."

    # Проверка наличия certbot
    if ! command -v certbot &> /dev/null; then
        echo "📦 Установка certbot..."
        sudo apt update
        sudo apt install -y certbot
    fi

    # Остановка nginx для получения сертификата
    echo "🛑 Остановка nginx для получения сертификата..."
    sudo systemctl stop nginx

    # Получение SSL сертификата
    echo "🔒 Получение SSL сертификата..."
    if sudo certbot certonly --standalone -d fan-club.kz -d www.fan-club.kz --non-interactive --agree-tos --email admin@fan-club.kz; then
        success_msg "SSL сертификат получен"

        # Создаем SSL конфигурацию
        sudo tee /etc/nginx/sites-available/fan-club > /dev/null << 'EOF'
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
        alias /var/www/myapp/eventsite/static/;
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

        success_msg "SSL конфигурация создана"

        # Активируем конфигурацию
        sudo ln -sf /etc/nginx/sites-available/fan-club /etc/nginx/sites-enabled/
        sudo rm -f /etc/nginx/sites-enabled/fan-club.kz

        # Проверяем и запускаем nginx
        if nginx -t; then
            sudo systemctl start nginx
            if systemctl is-active --quiet nginx; then
                success_msg "nginx запущен с SSL"
                echo ""
                success_msg "✅ SSL конфигурация установлена! Сайт доступен по https://fan-club.kz"
            else
                error_msg "nginx не запустился"
            fi
        else
            error_msg "Ошибка в SSL конфигурации nginx"
        fi
    else
        error_msg "Не удалось получить SSL сертификат"
        # Возвращаем nginx в исходное состояние
        sudo systemctl start nginx
    fi
}

# Основная функция
main() {
    echo "🔍 Диагностика SSL сертификатов и nginx конфигурации"
    echo "Дата: $(date)"
    echo ""

    # Проверка прав root
    if [[ $EUID -eq 0 ]]; then
        error_msg "Этот скрипт не должен запускаться от root. Используйте sudo для отдельных команд."
        exit 1
    fi

    # Выполнение проверок
    check_nginx_status
    check_ssl_certificates
    check_website_access
    analyze_problem

    # Предложение автоматического исправления если есть SSL проблемы
    if [[ " ${solutions[@]} " =~ " ssl_fix " ]]; then
        echo ""
        fix_ssl_problems
    fi

    print_separator
    echo "🏁 Диагностика завершена!"
    echo ""
    echo "💡 Если проблемы остались, проверьте:"
    echo "   - Django сервер: source venv/bin/activate && python manage.py runserver 0.0.0.0:8000"
    echo "   - Логи nginx: sudo tail -f /var/log/nginx/error.log"
    echo "   - Статус nginx: sudo systemctl status nginx"
}

# Запуск основной функции
main