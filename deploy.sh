#!/bin/bash

# UnitySphere Deployment Script
# Usage: ./deploy.sh [environment] [options]

set -e  # Exit on error

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Конфигурация по умолчанию
ENVIRONMENT=${1:-production}
PROJECT_NAME="unitysphere"
PROJECT_DIR="/var/www/unitysphere"
VIRTUALENV_DIR="/var/www/venv_unitysphere"
LOG_DIR="/var/log/unitysphere"
BACKUP_DIR="/var/backups/unitysphere"

# Функции для логирования
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

# Проверка прав root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Этот скрипт нужно запускать с правами root"
        exit 1
    fi
}

# Проверка окружения
check_environment() {
    log_info "Проверка окружения: $ENVIRONMENT"

    if [[ ! "$ENVIRONMENT" =~ ^(production|staging|development)$ ]]; then
        log_error "Неверное окружение. Доступные: production, staging, development"
        exit 1
    fi
}

# Создание бэкапа
create_backup() {
    log_info "Создание бэкапа..."

    BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
    BACKUP_PATH="$BACKUP_DIR/backup_$BACKUP_DATE"

    # Создаем директорию для бэкапа
    mkdir -p "$BACKUP_PATH"

    # Бэкап базы данных
    if [[ "$ENVIRONMENT" == "production" ]]; then
        log_info "Бэкап базы данных PostgreSQL..."
        sudo -u postgres pg_dump unitysphere_prod | gzip > "$BACKUP_PATH/database.sql.gz"
    else
        log_info "Бэкап базы данных SQLite..."
        cp "$PROJECT_DIR/db.sqlite3" "$BACKUP_PATH/" 2>/dev/null || true
    fi

    # Бэкап медиа файлов
    if [[ -d "$PROJECT_DIR/media" ]]; then
        log_info "Бэкап медиа файлов..."
        tar -czf "$BACKUP_PATH/media.tar.gz" -C "$PROJECT_DIR" media/
    fi

    # Бэкап настроек
    cp "$PROJECT_DIR/.env" "$BACKUP_PATH/" 2>/dev/null || true
    cp "$PROJECT_DIR/requirements.txt" "$BACKUP_PATH/" 2>/dev/null || true

    log_success "Бэкап создан: $BACKUP_PATH"

    # Удаляем старые бэкапы (оставляем последние 10)
    find "$BACKUP_DIR" -type d -name "backup_*" | sort -r | tail -n +11 | xargs rm -rf 2>/dev/null || true
}

# Обновление кода
update_code() {
    log_info "Обновление кода..."

    # Переходим в директорию проекта
    cd "$PROJECT_DIR" 2>/dev/null || {
        log_error "Директория проекта не найдена: $PROJECT_DIR"
        exit 1
    }

    # Получаем последние изменения из git
    if [[ -d ".git" ]]; then
        log_info "Получение изменений из Git..."
        git fetch origin
        git reset --hard origin/main
    else
        log_warning "Git репозиторий не найден"
    fi

    log_success "Код обновлен"
}

# Установка зависимостей
install_dependencies() {
    log_info "Установка зависимостей..."

    # Активируем виртуальное окружение
    if [[ -d "$VIRTUALENV_DIR" ]]; then
        source "$VIRTUALENV_DIR/bin/activate"
    else
        log_warning "Виртуальное окружение не найдено: $VIRTUALENV_DIR"
    fi

    # Обновляем pip
    pip install --upgrade pip

    # Устанавливаем зависимости
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
    fi

    if [[ -f "requirements_production.txt" ]]; then
        pip install -r requirements_production.txt
    fi

    log_success "Зависимости установлены"
}

# Миграции базы данных
migrate_database() {
    log_info "Миграция базы данных..."

    cd "$PROJECT_DIR"
    if [[ -f "manage.py" ]]; then
        # Создаем миграции если нужно
        python manage.py makemigrations --noinput

        # Применяем миграции
        python manage.py migrate --noinput

        log_success "Миграции завершены"
    else
        log_warning "manage.py не найден"
    fi
}

# Сбор статики
collect_static() {
    log_info "Сбор статических файлов..."

    cd "$PROJECT_DIR"
    if [[ -f "manage.py" ]]; then
        python manage.py collectstatic --noinput
        log_success "Статические файлы собраны"
    else
        log_warning "manage.py не найден"
    fi
}

# Прогрев кэша
warm_cache() {
    log_info "Прогрев кэша..."

    cd "$PROJECT_DIR"
    if [[ -f "manage.py" ]]; then
        python manage.py shell -c "
try:
    from core.cache import cache_warmer
    cache_warmer.warm_all()
    print('Cache warmed successfully')
except Exception as e:
    print(f'Error warming cache: {e}')
" 2>/dev/null || log_warning "Не удалось прогреть кэш"
    fi

    log_success "Кэш прогрет"
}

# Перезапуск сервисов
restart_services() {
    log_info "Перезапуск сервисов..."

    if systemctl is-active --quiet nginx 2>/dev/null; then
        systemctl reload nginx
        log_success "Nginx перезапущен"
    fi

    if systemctl is-active --quiet gunicorn 2>/dev/null; then
        systemctl restart gunicorn
        log_success "Gunicorn перезапущен"
    fi

    if systemctl is-active --quiet redis 2>/dev/null; then
        systemctl restart redis
        log_success "Redis перезапущен"
    fi
}

# Проверка здоровья
health_check() {
    log_info "Проверка здоровья системы..."

    # Проверка Gunicorn
    if pgrep -f "gunicorn" > /dev/null 2>/dev/null; then
        log_info "Gunicorn работает"
    else
        log_warning "Gunicorn не запущен"
    fi

    # Проверка Nginx
    if systemctl is-active --quiet nginx 2>/dev/null; then
        log_info "Nginx работает"
    else
        log_warning "Nginx не запущен"
    fi

    # Проверка Redis
    if systemctl is-active --quiet redis 2>/dev/null; then
        log_info "Redis работает"
    else
        log_warning "Redis не запущен"
    fi

    # HTTP проверка
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null || echo "000")
    if [[ "$HTTP_STATUS" == "200" ]] || [[ "$HTTP_STATUS" == "302" ]]; then
        log_success "Система работает корректно"
        return 0
    else
        log_warning "HTTP проверка не пройдена: $HTTP_STATUS"
        return 1
    fi
}

# Очистка
cleanup() {
    log_info "Очистка временных файлов..."

    # Очистка pip cache
    if [[ -d "$VIRTUALENV_DIR" ]]; then
        source "$VIRTUALENV_DIR/bin/activate"
        pip cache purge
    fi

    # Очистка старых логов
    if [[ -d "$LOG_DIR" ]]; then
        find "$LOG_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null || true
    fi

    # Очистка Django cache
    if [[ -d "$PROJECT_DIR" ]]; then
        cd "$PROJECT_DIR"
        if [[ -f "manage.py" ]]; then
            python manage.py clearsessions 2>/dev/null || true
        fi
    fi

    log_success "Очистка завершена"
}

# Откат изменений
rollback() {
    log_warning "Откат изменений..."

    # Находим последний бэкап
    if [[ -d "$BACKUP_DIR" ]]; then
        LATEST_BACKUP=$(find "$BACKUP_DIR" -type d -name "backup_*" 2>/dev/null | sort | tail -1)

        if [[ -z "$LATEST_BACKUP" ]]; then
            log_error "Бэкап не найден"
            exit 1
        fi

        log_info "Восстановление из: $LATEST_BACKUP"

        # Восстановление базы данных
        if [[ -f "$LATEST_BACKUP/database.sql.gz" ]]; then
            log_info "Восстановление базы данных..."
            gunzip -c "$LATEST_BACKUP/database.sql.gz" | sudo -u postgres psql unitysphere_prod 2>/dev/null || true
        fi

        # Восстановление медиа файлов
        if [[ -f "$LATEST_BACKUP/media.tar.gz" ]]; then
            log_info "Восстановление медиа файлов..."
            tar -xzf "$LATEST_BACKUP/media.tar.gz" -C "$PROJECT_DIR/" 2>/dev/null || true
        fi

        restart_services
        health_check
    else
        log_error "Директория бэкапов не найдена"
    fi
}

# Основная функция
main() {
    log_info "Начало деплоя UnitySphere в $ENVIRONMENT"

    # Выполняем шаги деплоя
    check_root
    check_environment

    if [[ "$ENVIRONMENT" == "production" ]]; then
        create_backup
    fi

    update_code
    install_dependencies
    migrate_database
    collect_static

    if [[ "$ENVIRONMENT" == "production" ]]; then
        warm_cache
    fi

    restart_services

    # Проверка здоровья
    if health_check; then
        cleanup
        log_success "Деплой завершен успешно!"
    else
        log_error "Деплой завершился с ошибками"
        if [[ "$ENVIRONMENT" == "production" ]]; then
            log_warning "Выполнение отката..."
            rollback
        fi
        exit 1
    fi
}

# Показываем справку
show_help() {
    echo "UnitySphere Deployment Script"
    echo ""
    echo "Использование:"
    echo "  $0 [environment] [options]"
    echo ""
    echo "Окружения:"
    echo "  production   - Продакшен сервер"
    echo "  staging      - Тестовый сервер"
    echo "  development  - Разработка"
    echo ""
    echo "Опции:"
    echo "  rollback     - Откатить последний деплой"
    echo "  help         - Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0 production    - Деплой на продакшен"
    echo "  $0 staging       - Деплой на тестовый сервер"
    echo "  $0 rollback      - Откатить изменения"
}

# Обработка аргументов
case "$1" in
    "help"|"-h"|"--help")
        show_help
        exit 0
        ;;
    "rollback")
        rollback
        exit 0
        ;;
    *)
        main
        ;;
esac