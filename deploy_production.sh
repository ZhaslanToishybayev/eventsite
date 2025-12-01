#!/bin/bash
# 🚀 UnitySphere AI Production Deployment Script
# Быстрое развертывание production окружения

set -e

echo "🚀 UnitySphere AI Production Deployment"
echo "========================================"

# 🔧 Конфигурация
PROJECT_DIR="/var/www/myapp/eventsite"
PROJECT_NAME="unitysphere"
USER="www-data"
GROUP="www-data"

# 🎯 Цели развертывания
DEPLOY_NGINX=${1:-false}
DEPLOY_GUNICORN=${2:-false}
DEPLOY_SSL=${3:-false}
SETUP_SECURITY=${4:-false}

# 📋 Функции

setup_directories() {
    echo "📁 Создание директорий..."
    sudo mkdir -p /var/log/gunicorn
    sudo mkdir -p /var/run/gunicorn
    sudo mkdir -p /var/www/myapp/eventsite/logs
    sudo mkdir -p /var/www/myapp/eventsite/media
    sudo mkdir -p /var/www/myapp/eventsite/staticfiles

    sudo chown -R $USER:$GROUP /var/log/gunicorn
    sudo chown -R $USER:$GROUP /var/run/gunicorn
    sudo chown -R $USER:$GROUP /var/www/myapp/eventsite/media
    sudo chown -R $USER:$GROUP /var/www/myapp/eventsite/staticfiles
    sudo chmod -R 755 /var/www/myapp/eventsite
}

install_dependencies() {
    echo "📦 Установка production зависимостей..."
    cd $PROJECT_DIR

    # 🐍 Python зависимости
    source venv/bin/activate

    # 🚀 Production сервер
    pip install gunicorn[gevent]

    # 📊 Мониторинг
    pip install psutil

    # 🔒 Безопасность
    pip install django-secure

    # 📁 Статика
    pip install whitenoise

    deactivate
}

setup_gunicorn() {
    if [ "$DEPLOY_GUNICORN" = "true" ]; then
        echo "🦄 Настройка Gunicorn..."

        # 📝 Копируем systemd сервис
        sudo cp $PROJECT_DIR/unitysphere-gunicorn.service /etc/systemd/system/

        # 🔧 Настройка Gunicorn
        sudo chown root:root /etc/systemd/system/unitysphere-gunicorn.service
        sudo chmod 644 /etc/systemd/system/unitysphere-gunicorn.service

        # 🔄 Перезагрузка systemd
        sudo systemctl daemon-reload

        # 🚀 Запуск сервиса
        sudo systemctl enable unitysphere-gunicorn
        sudo systemctl start unitysphere-gunicorn

        # ✅ Проверка статуса
        sudo systemctl status unitysphere-gunicorn --no-pager -l
    fi
}

setup_nginx() {
    if [ "$DEPLOY_NGINX" = "true" ]; then
        echo "/nginx Настройка Nginx..."

        # 📝 Копируем конфиг
        sudo cp $PROJECT_DIR/nginx_unitysphere.conf /etc/nginx/sites-available/$PROJECT_NAME

        # 🔄 Активация сайта
        sudo ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/

        # ❌ Удаление default сайта
        sudo rm -f /etc/nginx/sites-enabled/default

        # ✅ Проверка конфигурации
        sudo nginx -t

        # 🚀 Перезагрузка Nginx
        sudo systemctl reload nginx
    fi
}

setup_ssl() {
    if [ "$DEPLOY_SSL" = "true" ]; then
        echo "🔐 Настройка SSL сертификатов..."

        # 📦 Установка Certbot
        sudo apt update
        sudo apt install -y certbot python3-certbot-nginx

        # 🔄 Получение SSL сертификата
        sudo certbot --nginx -d fan-club.kz -d www.fan-club.kz --non-interactive --agree-tos

        # 🕐 Автоматическая пролонгация
        sudo crontab -l | grep -v "certbot" | sudo crontab -
        echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
    fi
}

setup_security() {
    if [ "$SETUP_SECURITY" = "true" ]; then
        echo "🛡️ Настройка безопасности..."

        # 🔒 UFW Firewall
        sudo ufw allow 22/tcp    # SSH
        sudo ufw allow 80/tcp    # HTTP
        sudo ufw allow 443/tcp   # HTTPS
        sudo ufw --force enable

        # 🛡️ Fail2ban
        sudo apt install -y fail2ban

        # 📝 Конфигурация Fail2ban для Nginx
        sudo tee /etc/fail2ban/jail.d/nginx.conf > /dev/null <<EOF
[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-noscript]
enabled = true
port = http,https
filter = nginx-noscript
logpath = /var/log/nginx/access.log
maxretry = 6
bantime = 86400

[nginx-badbots]
enabled = true
port = http,https
filter = nginx-badbots
logpath = /var/log/nginx/access.log
maxretry = 2
bantime = 86400
EOF

        sudo systemctl enable fail2ban
        sudo systemctl start fail2ban
    fi
}

collect_static() {
    echo "📦 Сборка статики..."
    cd $PROJECT_DIR
    source venv/bin/activate

    # 🧹 Очистка старой статики
    rm -rf staticfiles/*

    # 📦 Сборка новой статики
    python manage.py collectstatic --noinput --clear

    deactivate

    # 🔒 Права доступа
    sudo chown -R $USER:$GROUP staticfiles/
    sudo chmod -R 755 staticfiles/
}

setup_monitoring() {
    echo "📊 Настройка мониторинга..."

    # 📝 Создание скрипта мониторинга
    sudo tee /usr/local/bin/unitysphere-monitor.sh > /dev/null <<EOF
#!/bin/bash
# UnitySphere AI Monitoring Script

PROJECT_DIR="$PROJECT_DIR"
LOG_FILE="/var/log/unitysphere-monitor.log"

echo "[$(date)] Monitoring UnitySphere AI..." >> $LOG_FILE

# 🔍 Health checks
if curl -f -s http://localhost/health/ > /dev/null; then
    echo "[$(date)] ✅ Application is healthy" >> $LOG_FILE
else
    echo "[$(date)] ❌ Application is down - restarting..." >> $LOG_FILE
    sudo systemctl restart unitysphere-gunicorn
fi

# 🔍 Nginx check
if systemctl is-active --quiet nginx; then
    echo "[$(date)] ✅ Nginx is running" >> $LOG_FILE
else
    echo "[$(date)] ❌ Nginx is down - restarting..." >> $LOG_FILE
    sudo systemctl restart nginx
fi

# 🔍 Gunicorn check
if systemctl is-active --quiet unitysphere-gunicorn; then
    echo "[$(date)] ✅ Gunicorn is running" >> $LOG_FILE
else
    echo "[$(date)] ❌ Gunicorn is down - restarting..." >> $LOG_FILE
    sudo systemctl restart unitysphere-gunicorn
fi

# 📊 Disk usage check
DISK_USAGE=$(df / | awk 'NR==2{printf "%.1f", $5}')
if (( $(echo "$DISK_USAGE > 90" | bc -l) )); then
    echo "[$(date)] ⚠️ Disk usage is high: ${DISK_USAGE}%" >> $LOG_FILE
fi

echo "[$(date)] Monitoring complete" >> $LOG_FILE
EOF

    sudo chmod +x /usr/local/bin/unitysphere-monitor.sh

    # 🕐 Cron job для мониторинга
    sudo crontab -l | grep -v "unitysphere-monitor" | sudo crontab -
    echo "*/5 * * * * /usr/local/bin/unitysphere-monitor.sh" | sudo crontab -
}

cleanup() {
    echo "🧹 Очистка временных файлов..."
    sudo apt autoremove -y
    sudo apt autoclean
}

# 🎯 Основной процесс развертывания

main() {
    echo "🎯 Начинаем развертывание UnitySphere AI..."

    # 📁 Подготовка директорий
    setup_directories

    # 📦 Зависимости
    install_dependencies

    # 📁 Сборка статики
    collect_static

    # 🦄 Gunicorn
    setup_gunicorn

    # 📝 Nginx
    setup_nginx

    # 🔐 SSL
    setup_ssl

    # 🛡️ Безопасность
    setup_security

    # 📊 Мониторинг
    setup_monitoring

    # 🧹 Очистка
    cleanup

    echo "🎉 UnitySphere AI Production Deployment завершен!"
    echo "=============================================="
    echo "🌐 Сайт доступен по адресу: https://fan-club.kz"
    echo "🤖 AI Chat: https://fan-club.kz"
    echo "📊 Health Check: https://fan-club.kz/health/"
    echo "🔍 Логи: /var/log/gunicorn/"
    echo ""
    echo "🛠️ Команды управления:"
    echo "sudo systemctl status unitysphere-gunicorn  # Статус приложения"
    echo "sudo systemctl restart unitysphere-gunicorn # Перезапуск приложения"
    echo "sudo nginx -t                               # Проверка Nginx конфигурации"
    echo "sudo systemctl restart nginx                 # Перезапуск Nginx"
}

# 🚀 Запуск
main "$@"