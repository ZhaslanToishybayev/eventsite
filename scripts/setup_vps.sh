#!/bin/bash

# UnitySphere VPS Setup Script for fan-club.kz
# Usage: ./setup_vps.sh

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Логирование
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка root прав
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Этот скрипт нужно запускать с правами root"
        exit 1
    fi
}

# Получение информации о системе
get_system_info() {
    log_info "Получение информации о системе..."

    # Определение дистрибутива
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VERSION=$VERSION_ID
    else
        log_error "Не удалось определить дистрибутив"
        exit 1
    fi

    log_info "OS: $OS"
    log_info "Version: $VERSION"

    # Проверка ресурсов
    CPU_CORES=$(nproc)
    RAM_GB=$(free -g | awk '/^Mem:/{print $2}')

    log_info "CPU cores: $CPU_CORES"
    log_info "RAM: ${RAM_GB}GB"

    # Проверка свободного места
    DISK_FREE=$(df -h / | awk 'NR==2 {print $4}')
    log_info "Free disk space: $DISK_FREE"

    # Проверка требований
    if [ "$RAM_GB" -lt 2 ]; then
        log_warning "Рекомендуется минимум 2GB RAM, у вас ${RAM_GB}GB"
    fi

    if [ "$CPU_CORES" -lt 2 ]; then
        log_warning "Рекомендуется минимум 2 CPU core, у вас $CPU_CORES"
    fi
}

# Установка системных зависимостей
install_system_packages() {
    log_info "Установка системных пакетов..."

    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        apt-get update
        apt-get install -y \
            curl \
            wget \
            git \
            nginx \
            certbot \
            python3-certbot-nginx \
            python3-pip \
            python3-venv \
            build-essential \
            libpq-dev \
            libmagic1 \
            gcc \
            postgresql-client \
            ufw \
            fail2ban \
            logrotate \
            cron \
            htop \
            net-tools
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        yum update -y
        yum install -y \
            curl \
            wget \
            git \
            nginx \
            certbot \
            python3 \
            python3-pip \
            python3-venv \
            gcc \
            postgresql \
            postgresql-devel \
            libmagic \
            firewalld \
            fail2ban \
            cronie \
            htop \
            net-tools
    else
        log_error "Неподдерживаемый дистрибутив"
        exit 1
    fi

    log_success "Системные пакеты установлены"
}

# Настройка firewall
setup_firewall() {
    log_info "Настройка firewall..."

    if command -v ufw &> /dev/null; then
        # Ubuntu/Debian
        ufw allow 22/tcp    # SSH
        ufw allow 80/tcp    # HTTP
        ufw allow 443/tcp   # HTTPS
        ufw --force enable
        log_success "UFW настроен"
    elif command -v firewall-cmd &> /dev/null; then
        # CentOS/RHEL
        systemctl start firewalld
        systemctl enable firewalld
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --reload
        log_success "Firewalld настроен"
    fi
}

# Настройка fail2ban
setup_fail2ban() {
    log_info "Настройка fail2ban..."

    if command -v fail2ban-client &> /dev/null; then
        systemctl enable fail2ban
        systemctl start fail2ban

        # Создаем конфиг для SSH
        cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
EOF

        systemctl restart fail2ban
        log_success "Fail2ban настроен"
    fi
}

# Установка Docker
install_docker() {
    log_info "Установка Docker..."

    if ! command -v docker &> /dev/null; then
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh

        # Добавляем пользователя в docker группу
        usermod -aG docker $SUDO_USER
        log_success "Docker установлен"
    else
        log_success "Docker уже установлен"
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_info "Установка Docker Compose..."

        COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
        curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose

        log_success "Docker Compose установлен"
    else
        log_success "Docker Compose уже установлен"
    fi
}

# Создание пользователей
create_users() {
    log_info "Создание пользователей..."

    # Создаем пользователя для приложения
    if ! id "unitysphere" &>/dev/null; then
        useradd -r -s /bin/bash -d /opt/unitysphere -m unitysphere
        usermod -aG docker unitysphere
        log_success "Пользователь unitysphere создан"
    else
        log_success "Пользователь unitysphere уже существует"
    fi

    # Создаем группы для логов
    if ! getent group unitysphere &>/dev/null; then
        groupadd unitysphere
    fi

    usermod -aG unitysphere unitysphere
    usermod -aG unitysphere $SUDO_USER
}

# Создание структуры директорий
setup_directories() {
    log_info "Создание структуры директорий..."

    # Директории для приложения
    mkdir -p /opt/unitysphere/{logs,backups,staticfiles,media}
    mkdir -p /var/log/unitysphere
    mkdir -p /var/www/unitysphere/{staticfiles,media}
    mkdir -p /backups/unitysphere

    # Права доступа
    chown -R unitysphere:unitysphere /opt/unitysphere
    chown -R www-data:www-data /var/www/unitysphere
    chown root:unitysphere /var/log/unitysphere
    chmod 755 /var/log/unitysphere
    chmod 755 /backups/unitysphere
    chmod 755 /opt/unitysphere

    log_success "Директории созданы"
}

# Настройка Nginx
setup_nginx() {
    log_info "Настройка Nginx..."

    systemctl enable nginx
    systemctl start nginx

    # Создаем директорию для сайтов
    mkdir -p /etc/nginx/sites-available
    mkdir -p /etc/nginx/sites-enabled

    # Проверяем default конфигурацию
    if [ -f /etc/nginx/sites-enabled/default ]; then
        rm /etc/nginx/sites-enabled/default
    fi

    # Создаем базовую конфигурацию
    cat > /etc/nginx/nginx.conf << 'EOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 10M;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Gzip
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

    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
EOF

    log_success "Nginx настроен"
}

# Настройка системы
setup_system() {
    log_info "Настройка системы..."

    # Увеличиваем лимиты
    cat >> /etc/security/limits.conf << 'EOF'
unitysphere soft nofile 65536
unitysphere hard nofile 65536
unitysphere soft nproc 65536
unitysphere hard nproc 65536
EOF

    # Настройка sysctl
    cat >> /etc/sysctl.conf << 'EOF'
# UnitySphere optimizations
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 1200
net.ipv4.tcp_max_tw_buckets = 200000
net.ipv4.ip_local_port_range = 10000 65000
vm.swappiness = 10
EOF

    sysctl -p

    # Настройка logrotate для UnitySphere
    cat > /etc/logrotate.d/unitysphere << 'EOF'
/var/log/unitysphere/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    su www-data unitysphere
}

/opt/unitysphere/logs/*.log {
    weekly
    missingok
    rotate 12
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

    log_success "Система настроена"
}

# Создание скриптов управления
create_management_scripts() {
    log_info "Создание скриптов управления..."

    # Скрипт для резервного копирования
    cat > /usr/local/bin/unitysphere-backup << 'EOF'
#!/bin/bash
# UnitySphere Backup Script

set -e

BACKUP_DIR="/backups/unitysphere"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/backup_$DATE"

mkdir -p "$BACKUP_PATH"

echo "Creating backup at $BACKUP_PATH"

# Backup database
if docker-compose -f /opt/unitysphere/docker-compose.production.yaml exec -t fnclub-db pg_dump -U postgres postgres > "$BACKUP_PATH/database.sql"; then
    echo "Database backup created"
else
    echo "Database backup failed"
fi

# Backup media files
if [ -d "/opt/unitysphere/media" ]; then
    tar -czf "$BACKUP_PATH/media.tar.gz" -C /opt/unitysphere media/
    echo "Media backup created"
fi

# Backup configuration
cp /opt/unitysphere/.env "$BACKUP_PATH/" 2>/dev/null || true
cp /opt/unitysphere/docker-compose.production.yaml "$BACKUP_PATH/" 2>/dev/null || true

# Cleanup old backups (keep last 10)
find "$BACKUP_DIR" -name "backup_*" -type d | sort -r | tail -n +11 | xargs rm -rf 2>/dev/null || true

echo "Backup completed: $BACKUP_PATH"
EOF

    chmod +x /usr/local/bin/unitysphere-backup

    # Health check скрипт
    cat > /usr/local/bin/unitysphere-health-check << 'EOF'
#!/bin/bash
# UnitySphere Health Check

URL="https://fan-club.kz/api/v1/ai/health/"
TIMEOUT=10

response=$(curl -s --connect-timeout $TIMEOUT $URL)
status=$(echo $response | grep -o '"overall_status":"[^"]*"' | cut -d'"' -f4)

if [ "$status" == "healthy" ]; then
    echo "Health check passed: $status"
    exit 0
else
    echo "Health check failed: $status"
    echo "Response: $response"
    exit 1
fi
EOF

    chmod +x /usr/local/bin/unitysphere-health-check

    # Скрипт для перезапуска
    cat > /usr/local/bin/unitysphere-restart << 'EOF'
#!/bin/bash
# UnitySphere Restart Script

echo "Restarting UnitySphere..."

cd /opt/unitysphere
docker-compose -f docker-compose.production.yaml restart fnclub

echo "Waiting for service to start..."
sleep 10

if /usr/local/bin/unitysphere-health-check; then
    echo "Service restarted successfully"
else
    echo "Health check failed after restart"
    exit 1
fi
EOF

    chmod +x /usr/local/bin/unitysphere-restart

    log_success "Скрипты управления созданы"
}

# Настройка cron jobs
setup_cron_jobs() {
    log_info "Настройка cron jobs..."

    # Создаем cron для unitysphere пользователя
    sudo -u unitysphere crontab -l 2>/dev/null > /tmp/unitysphere_cron || true

    # Добавляем задачи
    cat >> /tmp/unitysphere_cron << 'EOF'
# UnitySphere cron jobs
0 2 * * * /usr/local/bin/unitysphere-backup
*/10 * * * /usr/local/bin/unitysphere-health-check >> /var/log/unitysphere/health-check.log 2>&1
0 3 * * 0 docker system prune -f
EOF

    sudo -u unitysphere crontab /tmp/unitysphere_cron
    rm /tmp/unitysphere_cron

    # Включаем cron
    systemctl enable cron
    systemctl start cron

    log_success "Cron jobs настроены"
}

# Финальная проверка
final_check() {
    log_info "Финальная проверка..."

    echo ""
    echo "=== VPS Setup Complete ==="
    echo ""

    log_success "Системные службы:"
    systemctl is-active --quiet nginx && log_info "✓ Nginx: running" || log_warning("✗ Nginx: not running")
    systemctl is-active --quiet docker && log_info "✓ Docker: running" || log_warning("✗ Docker: not running")
    systemctl is-active --quiet fail2ban && log_info "✓ Fail2ban: running" || log_warning("✗ Fail2ban: not running")

    echo ""
    log_success "Пользователи и директории:"
    id unitysphere &>/dev/null && log_info "✓ unitysphere user: exists" || log_warning("✗ unitysphere user: missing")
    [ -d "/opt/unitysphere" ] && log_info "✓ Application directory: exists" || log_warning("✗ Application directory: missing")
    [ -d "/var/log/unitysphere" ] && log_info "✓ Log directory: exists" || log_warning("✗ Log directory: missing")

    echo ""
    log_success "Сетевые настройки:"
    ufw status | grep -q "Status: active" && log_info "✓ Firewall: active" || log_warning("✗ Firewall: inactive")
    netstat -tlnp | grep -q ":80 " && log_info "✓ HTTP port: open" || log_warning("✗ HTTP port: closed")
    netstat -tlnp | grep -q ":443 " && log_info "✓ HTTPS port: open" || log_warning("✗ HTTPS port: closed")

    echo ""
    log_success "Инструменты управления:"
    [ -x "/usr/local/bin/unitysphere-backup" ] && log_info "✓ Backup script: installed" || log_warning("✗ Backup script: missing")
    [ -x "/usr/local/bin/unitysphere-health-check" ] && log_info "✓ Health check script: installed" || log_warning("✗ Health check script: missing")

    echo ""
    echo "=== Next Steps ==="
    echo "1. Скопируйте проект UnitySphere в /opt/unitysphere"
    echo "2. Создайте .env.production файл с production настройками"
    echo "3. Запустите: sudo -u unitysphere bash deploy_production.sh"
    echo "4. Настройте SSL сертификат: sudo certbot --nginx -d fan-club.kz -d www.fan-club.kz"
    echo "5. Проверьте работу сайта: https://fan-club.kz"
    echo ""

    log_success "VPS setup completed successfully!"
}

# Основная функция
main() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}🚀 UnitySphere VPS Setup for fan-club.kz${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    check_root
    get_system_info
    install_system_packages
    setup_firewall
    setup_fail2ban
    install_docker
    create_users
    setup_directories
    setup_nginx
    setup_system
    create_management_scripts
    setup_cron_jobs
    final_check
}

# Обработка аргументов
case "$1" in
    "check")
        get_system_info
        ;;
    "firewall")
        setup_firewall
        ;;
    "docker")
        install_docker
        ;;
    "nginx")
        setup_nginx
        ;;
    "users")
        create_users
        setup_directories
        ;;
    *)
        main
        ;;
esac