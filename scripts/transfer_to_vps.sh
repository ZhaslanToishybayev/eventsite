#!/bin/bash

# UnitySphere Project Transfer Script
# Usage: ./transfer_to_vps.sh [vps_ip] [ssh_port] [username]

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Функции логирования
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

# Показываем помощь
show_help() {
    echo "UnitySphere Project Transfer Script"
    echo ""
    echo "Usage: $0 [vps_ip] [ssh_port] [username]"
    echo ""
    echo "Examples:"
    echo "  $0 123.45.67.89 22 root"
    echo "  $0 123.45.67.89 2222 admin"
    echo "  $0 your-domain.com 22 root"
    echo ""
    echo "Parameters:"
    echo "  vps_ip      - VPS IP address or domain name"
    echo "  ssh_port    - SSH port (default: 22)"
    echo "  username    - SSH username (default: root)"
    echo ""
    echo "Prerequisites:"
    echo "  1. SSH access to VPS with sudo privileges"
    echo "  2. Docker and required packages already installed on VPS"
    echo "  3. .env.production file configured"
    echo ""
    echo "The script will:"
    echo "  1. Transfer project files to VPS"
    echo "  2. Set up proper permissions"
    echo "  3. Copy configuration files"
    echo "  4. Run initial deployment"
}

# Проверка аргументов
if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    show_help
    exit 0
fi

if [[ $# -lt 1 ]]; then
    log_error "VPS IP address is required!"
    echo ""
    show_help
    exit 1
fi

# Параметры
VPS_IP="$1"
SSH_PORT="${2:-22}"
USERNAME="${3:-root}"

PROJECT_NAME="unitysphere"
LOCAL_PROJECT_PATH="$(pwd)"
REMOTE_PROJECT_PATH="/opt/unitysphere"
BACKUP_PATH="/backups/unitysphere"

# Проверка что мы в правильной директории
if [[ ! -f "manage.py" ]] || [[ ! -f "docker-compose.yaml" ]]; then
    log_error "This script must be run from the UnitySphere project root directory!"
    exit 1
fi

# Проверка наличия .env.production
if [[ ! -f ".env.production" ]]; then
    log_warning ".env.production file not found!"
    log_info "1. Run: python3 scripts/generate_production_secrets.py > .env.production"
    log_info "2. Edit .env.production with your production values"
    log_info "3. Run this script again"
    exit 1
fi

# Функция для выполнения команд на VPS
ssh_exec() {
    ssh -p "$SSH_PORT" "$USERNAME@$VPS_IP" "$1"
}

# Функция для копирования файлов на VPS
scp_file() {
    scp -P "$SSH_PORT" "$1" "$USERNAME@$VPS_IP:$2"
}

# Функция для копирования директорий на VPS
scp_dir() {
    scp -P "$SSH_PORT" -r "$1" "$USERNAME@$VPS_IP:$2"
}

# Проверка подключения к VPS
test_connection() {
    log_info "Testing connection to $USERNAME@$VPS_IP:$SSH_PORT..."

    if ssh -p "$SSH_PORT" -o ConnectTimeout=10 "$USERNAME@$VPS_IP" "echo 'Connection successful'"; then
        log_success "Connection established"
    else
        log_error "Cannot connect to VPS. Please check:"
        log_error "1. IP address: $VPS_IP"
        log_error "2. SSH port: $SSH_PORT"
        log_error "3. Username: $USERNAME"
        log_error "4. SSH key or password authentication"
        exit 1
    fi
}

# Проверка прав root
check_sudo() {
    log_info "Checking sudo privileges..."

    if ssh_exec "sudo -n true 2>/dev/null || sudo -v"; then
        log_success "Sudo privileges confirmed"
    else
        log_error "Sudo privileges required for user: $USERNAME"
        exit 1
    fi
}

# Проверка установленных пакетов
check_prerequisites() {
    log_info "Checking prerequisites on VPS..."

    # Проверка Docker
    if ssh_exec "command -v docker" >/dev/null 2>&1; then
        log_success "Docker is installed"
    else
        log_error "Docker is not installed on VPS"
        log_info "Run: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
        exit 1
    fi

    # Проверка Docker Compose
    if ssh_exec "command -v docker-compose" >/dev/null 2>&1; then
        log_success "Docker Compose is installed"
    else
        log_error "Docker Compose is not installed on VPS"
        log_info "Install Docker Compose before running this script"
        exit 1
    fi

    # Проверка пользователя unitysphere
    if ssh_exec "id unitysphere" >/dev/null 2>&1; then
        log_success "UnitySphere user exists"
    else
        log_error "UnitySphere user does not exist"
        log_info "Run setup_vps.sh script first or create user manually:"
        log_info "sudo useradd -r -s /bin/bash -d /opt/unitysphere -m unitysphere"
        log_info "sudo usermod -aG docker unitysphere"
        exit 1
    fi
}

# Создание резервной копии существующего проекта
backup_existing_project() {
    log_info "Checking for existing project on VPS..."

    if ssh_exec "test -d $REMOTE_PROJECT_PATH"; then
        log_warning "Existing project found on VPS"

        # Создаем резервную копию
        BACKUP_DIR="$BACKUP_PATH/project_backup_$(date +%Y%m%d_%H%M%S)"
        log_info "Creating backup: $BACKUP_DIR"

        ssh_exec "sudo mkdir -p $BACKUP_DIR"
        ssh_exec "sudo cp -r $REMOTE_PROJECT_PATH/* $BACKUP_DIR/ 2>/dev/null || true"
        ssh_exec "sudo chown -R unitysphere:unitysphere $BACKUP_DIR"

        log_success "Backup created: $BACKUP_DIR"
    fi
}

# Перенос проекта
transfer_project() {
    log_info "Transferring project files to VPS..."

    # Создаем директорию проекта
    ssh_exec "sudo mkdir -p $REMOTE_PROJECT_PATH"
    ssh_exec "sudo chown unitysphere:unitysphere $REMOTE_PROJECT_PATH"

    # Копируем основные файлы
    local files_to_copy=(
        "manage.py"
        "requirements.txt"
        "requirements.production.txt"
        "docker-compose.yaml"
        "docker-compose.production.yaml"
        ".env.production"
        "scripts/deploy_production.sh"
        "scripts/generate_production_secrets.py"
        "scripts/setup_vps.sh"
        "nginx/fan-club.kz.conf"
        "core/settings_production.py"
    )

    for file in "${files_to_copy[@]}"; do
        if [[ -f "$file" ]]; then
            log_info "Copying $file..."
            scp_file "$file" "$REMOTE_PROJECT_PATH/"
        else
            log_warning "File not found: $file"
        fi
    done

    # Копируем директории
    local dirs_to_copy=(
        "accounts"
        "agents"
        "ai_consultant"
        "api"
        "clubs"
        "core"
        "static"
        "templates"
        "media"
        "scripts"
        "nginx"
    )

    for dir in "${dirs_to_copy[@]}"; do
        if [[ -d "$dir" ]]; then
            log_info "Copying directory $dir..."
            scp_dir "$dir" "$REMOTE_PROJECT_PATH/"
        else
            log_warning "Directory not found: $dir"
        fi
    done

    # Копируем документацию
    local docs_to_copy=(
        "DEPLOYMENT_GUIDE.md"
        "PRODUCTION_DEPLOYMENT_CHECKLIST.md"
        "QUICK_START_PRODUCTION.md"
        "PRODUCTION_READY_SUMMARY.md"
    )

    for doc in "${docs_to_copy[@]}"; do
        if [[ -f "$doc" ]]; then
            log_info "Copying documentation $doc..."
            scp_file "$doc" "$REMOTE_PROJECT_PATH/"
        fi
    done

    # Устанавливаем права
    ssh_exec "sudo chown -R unitysphere:unitysphere $REMOTE_PROJECT_PATH"
    ssh_exec "sudo chmod 755 $REMOTE_PROJECT_PATH/scripts/*.sh"
    ssh_exec "sudo chmod 600 $REMOTE_PROJECT_PATH/.env.production"
}

# Настройка окружения на VPS
setup_environment() {
    log_info "Setting up environment on VPS..."

    # Копируем .env.production в правильное место
    ssh_exec "sudo cp $REMOTE_PROJECT_PATH/.env.production $REMOTE_PROJECT_PATH/.env"

    # Создаем необходимые директории
    ssh_exec "sudo mkdir -p $REMOTE_PROJECT_PATH/{logs,backups,staticfiles,media}"
    ssh_exec "sudo mkdir -p /var/log/unitysphere"
    ssh_exec "sudo mkdir -p /var/www/unitysphere/{staticfiles,media}"
    ssh_exec "sudo mkdir -p $BACKUP_PATH"

    # Устанавливаем права
    ssh_exec "sudo chown -R unitysphere:unitysphere $REMOTE_PROJECT_PATH"
    ssh_exec "sudo chown -R www-data:www-data /var/www/unitysphere"
    ssh_exec "sudo chown root:unitysphere /var/log/unitysphere"
    ssh_exec "sudo chmod 755 /var/log/unitysphere"
    ssh_exec "sudo chmod 755 $BACKUP_PATH"
}

# Запуск деплоя
deploy_project() {
    log_info "Starting deployment..."

    # Переключаемся на пользователя unitysphere и запускаем деплой
    ssh_exec "sudo -u unitysphere bash -c 'cd $REMOTE_PROJECT_PATH && bash scripts/deploy_production.sh'"

    log_success "Deployment completed!"
}

# Проверка работоспособности
verify_deployment() {
    log_info "Verifying deployment..."

    # Проверка Docker контейнеров
    log_info "Checking Docker containers..."
    ssh_exec "docker-compose -f $REMOTE_PROJECT_PATH/docker-compose.production.yaml ps"

    # Проверка статуса сервиса
    log_info "Checking service status..."
    ssh_exec "sudo systemctl status unitysphere" || log_warning "Systemd service not configured yet"

    # Проверка health endpoint (если nginx настроен)
    log_info "Testing health endpoint..."
    local health_check=$(ssh_exec "curl -s http://localhost:8000/api/v1/ai/health/ || echo 'Service not accessible'")
    if [[ "$health_check" == *"healthy"* ]]; then
        log_success "Health check passed"
    else
        log_warning "Health check failed or service not ready"
        log_info "This is normal if nginx is not configured yet"
    fi
}

# Финальные инструкции
show_final_instructions() {
    echo ""
    echo "========================================"
    echo "🎉 Project transfer completed!"
    echo "========================================"
    echo ""
    echo "📁 Project location on VPS:"
    echo "   $REMOTE_PROJECT_PATH"
    echo ""
    echo "🔧 Next steps:"
    echo "1. Configure SSL certificate:"
    echo "   sudo certbot --nginx -d fan-club.kz -d www.fan-club.kz"
    echo ""
    echo "2. Set up monitoring (if not done):"
    echo "   sudo bash $REMOTE_PROJECT_PATH/scripts/setup_monitoring.sh"
    echo ""
    echo "3. Set up systemd service (if not done):"
    echo "   sudo bash $REMOTE_PROJECT_PATH/scripts/setup_systemd_service.sh"
    echo ""
    echo "4. Test your application:"
    echo "   curl https://fan-club.kz/api/v1/ai/health/"
    echo ""
    echo "📚 Documentation available:"
    echo "   $REMOTE_PROJECT_PATH/DEPLOYMENT_GUIDE.md"
    echo "   $REMOTE_PROJECT_PATH/QUICK_START_PRODUCTION.md"
    echo ""
    echo "🛠️ Management commands:"
    echo "   # Check logs"
    echo "   sudo docker-compose -f $REMOTE_PROJECT_PATH/docker-compose.production.yaml logs -f"
    echo ""
    echo "   # Health check"
    echo "   /usr/local/bin/unitysphere-health-check"
    echo ""
    echo "   # Backup"
    echo "   /usr/local/bin/unitysphere-backup"
    echo ""
    echo "========================================"
}

# Основная функция
main() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}🚀 UnitySphere Project Transfer${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    log_info "VPS: $USERNAME@$VPS_IP:$SSH_PORT"
    log_info "Local path: $LOCAL_PROJECT_PATH"
    log_info "Remote path: $REMOTE_PROJECT_PATH"
    echo ""

    test_connection
    check_sudo
    check_prerequisites
    backup_existing_project
    transfer_project
    setup_environment
    deploy_project
    verify_deployment
    show_final_instructions
}

# Запускаем основную функцию
main "$@"