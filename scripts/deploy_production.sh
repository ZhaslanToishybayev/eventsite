#!/bin/bash
#
# Скрипт автоматического деплоя UnitySphere в production
# Использование: ./scripts/deploy_production.sh [options]
#

set -e

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Конфигурация
DJANGO_SETTINGS_MODULE="core.settings_production"
BACKUP_BEFORE_DEPLOY=true
RUN_MIGRATIONS=true
COLLECT_STATIC=true
RESTART_SERVICES=true

# Функция логирования
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Функция для подтверждения
confirm() {
    local message=$1
    read -p "$(echo -e ${YELLOW}$message${NC}) (y/n): " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# Заголовок
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🚀 UnitySphere Production Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Проверка прав
if [ "$EUID" -eq 0 ]; then 
    log_warning "Не рекомендуется запускать от root"
fi

# Проверка что мы в правильной директории
if [ ! -f "manage.py" ]; then
    log_error "Ошибка: manage.py не найден!"
    log_error "Запустите скрипт из корня проекта"
    exit 1
fi

# Проверка .env файла
if [ ! -f ".env" ]; then
    log_error "Ошибка: .env файл не найден!"
    exit 1
fi

# Проверка критических переменных
source .env
if [ -z "$DJANGO_SECRET_KEY" ] || [ "$DJANGO_SECRET_KEY" == "your-secret-key-here" ]; then
    log_error "DJANGO_SECRET_KEY не настроен в .env!"
    exit 1
fi

if [ -z "$POSTGRES_PASSWORD" ]; then
    log_error "POSTGRES_PASSWORD не настроен в .env!"
    exit 1
fi

log_success "Проверка окружения пройдена"
echo ""

# Показываем текущую конфигурацию
echo -e "${BLUE}📋 Текущая конфигурация:${NC}"
echo "   DEBUG: ${DEBUG:-False}"
echo "   Database: PostgreSQL"
echo "   Migrations: $RUN_MIGRATIONS"
echo "   Static files: $COLLECT_STATIC"
echo "   Backup: $BACKUP_BEFORE_DEPLOY"
echo ""

# Подтверждение
if ! confirm "Продолжить деплой в production?"; then
    log_warning "Деплой отменен"
    exit 0
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🔄 Начинаем деплой...${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Шаг 1: Git pull (если используется)
if [ -d ".git" ]; then
    log_info "Обновление кода из Git..."
    
    # Проверка изменений
    if ! git diff-index --quiet HEAD --; then
        log_warning "Есть незакоммиченные изменения!"
        if ! confirm "Продолжить без сохранения изменений?"; then
            log_error "Деплой отменен. Закоммитьте изменения."
            exit 1
        fi
    fi
    
    CURRENT_BRANCH=$(git branch --show-current)
    log_info "Текущая ветка: $CURRENT_BRANCH"
    
    if confirm "Выполнить git pull?"; then
        git pull origin $CURRENT_BRANCH
        log_success "Код обновлен"
    fi
fi

echo ""

# Шаг 2: Backup базы данных
if [ "$BACKUP_BEFORE_DEPLOY" = true ]; then
    log_info "Создание backup базы данных..."
    
    if [ -f "scripts/backup_database.sh" ]; then
        bash scripts/backup_database.sh
        log_success "Backup создан"
    else
        log_warning "Скрипт backup не найден, пропускаем..."
    fi
fi

echo ""

# Шаг 3: Остановка старых контейнеров (если нужно)
log_info "Проверка Docker контейнеров..."
if docker compose ps | grep -q "Up"; then
    log_info "Контейнеры запущены"
else
    log_warning "Контейнеры не запущены, запускаем..."
    docker compose up -d
    sleep 5
fi

echo ""

# Шаг 4: Обновление зависимостей
log_info "Проверка и установка зависимостей..."

if [ -f "requirements.txt" ]; then
    log_info "Установка Python зависимостей..."
    docker compose exec -T fnclub pip install -r /proj/requirements.txt --no-cache-dir
    log_success "Зависимости установлены"
fi

echo ""

# Шаг 5: Миграции базы данных
if [ "$RUN_MIGRATIONS" = true ]; then
    log_info "Применение миграций базы данных..."
    
    # Проверка pending migrations
    PENDING=$(docker compose exec -T fnclub python /proj/manage.py showmigrations --plan 2>&1 | grep "\[ \]" | wc -l)
    
    if [ "$PENDING" -gt 0 ]; then
        log_warning "Найдено $PENDING pending миграций"
        docker compose exec -T fnclub python /proj/manage.py migrate --noinput
        log_success "Миграции применены"
    else
        log_success "Миграции уже применены"
    fi
fi

echo ""

# Шаг 6: Сборка статических файлов
if [ "$COLLECT_STATIC" = true ]; then
    log_info "Сборка статических файлов..."
    docker compose exec -T fnclub python /proj/manage.py collectstatic --noinput --clear
    log_success "Статические файлы собраны"
fi

echo ""

# Шаг 7: Проверка системы
log_info "Проверка Django конфигурации..."
docker compose exec -T fnclub python /proj/manage.py check --deploy 2>&1 | tee /tmp/django_check.log

if grep -q "ERROR" /tmp/django_check.log; then
    log_error "Найдены ошибки в конфигурации!"
    log_error "Проверьте вывод выше"
    
    if ! confirm "Продолжить несмотря на ошибки?"; then
        log_error "Деплой отменен"
        exit 1
    fi
else
    log_success "Проверка конфигурации пройдена"
fi

echo ""

# Шаг 8: Перезапуск сервисов
if [ "$RESTART_SERVICES" = true ]; then
    log_info "Перезапуск сервисов..."
    
    # Graceful restart
    docker compose restart fnclub
    
    # Ждем пока сервис поднимется
    log_info "Ожидание запуска сервиса..."
    sleep 10
    
    # Проверка что сервис запустился
    if docker compose ps fnclub | grep -q "Up"; then
        log_success "Сервис запущен"
    else
        log_error "Ошибка запуска сервиса!"
        docker compose logs --tail 50 fnclub
        exit 1
    fi
fi

echo ""

# Шаг 9: Health check
log_info "Проверка работоспособности..."

# Даем время на полный запуск
sleep 5

# Проверяем health endpoint
HEALTH_URL="http://localhost:8001/api/v1/ai/health/"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    log_success "Health check пройден (HTTP $HTTP_CODE)"
else
    log_warning "Health check не прошел (HTTP $HTTP_CODE)"
    log_warning "Проверьте логи: docker compose logs fnclub"
fi

echo ""

# Шаг 10: Статистика
log_info "Сбор статистики..."

USERS=$(docker compose exec -T fnclub-db psql -U postgres -d postgres -t -c "SELECT COUNT(*) FROM accounts_user;" 2>/dev/null | tr -d ' ' || echo "N/A")
CLUBS=$(docker compose exec -T fnclub-db psql -U postgres -d postgres -t -c "SELECT COUNT(*) FROM clubs_club;" 2>/dev/null | tr -d ' ' || echo "N/A")
SESSIONS=$(docker compose exec -T fnclub-db psql -U postgres -d postgres -t -c "SELECT COUNT(*) FROM ai_consultant_chatsession;" 2>/dev/null | tr -d ' ' || echo "N/A")

echo ""
echo -e "${BLUE}📊 Статистика после деплоя:${NC}"
echo "   Пользователей: $USERS"
echo "   Клубов: $CLUBS"
echo "   AI сессий: $SESSIONS"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Деплой завершен успешно!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Финальные инструкции
echo -e "${YELLOW}📝 Следующие шаги:${NC}"
echo "   1. Проверьте сайт в браузере"
echo "   2. Проверьте логи: docker compose logs -f fnclub"
echo "   3. Мониторьте ошибки первые 24 часа"
echo "   4. Проверьте Google OAuth: /accounts/google/login/"
echo ""

# Сохранение информации о деплое
DEPLOY_INFO="/tmp/unitysphere_deploy_$(date +%Y%m%d_%H%M%S).log"
cat > $DEPLOY_INFO << EOF
UnitySphere Deployment
=====================
Date: $(date)
User: $(whoami)
Branch: $(git branch --show-current 2>/dev/null || echo "N/A")
Commit: $(git rev-parse HEAD 2>/dev/null || echo "N/A")
Status: SUCCESS
Users: $USERS
Clubs: $CLUBS
AI Sessions: $SESSIONS
EOF

log_success "Лог деплоя сохранен: $DEPLOY_INFO"
echo ""
