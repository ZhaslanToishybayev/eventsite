#!/bin/bash
#
# Скрипт установки systemd service для UnitySphere
# Использование: sudo ./scripts/setup_systemd_service.sh
#

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}⚙️  Установка systemd service${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Проверка root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Этот скрипт должен запускаться от root${NC}"
    echo "   Используйте: sudo $0"
    exit 1
fi

# Конфигурация
SERVICE_NAME="unitysphere"
PROJECT_DIR="/opt/unitysphere"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo -e "${YELLOW}📋 Конфигурация:${NC}"
echo "   Service name: $SERVICE_NAME"
echo "   Project directory: $PROJECT_DIR"
echo "   Service file: $SERVICE_FILE"
echo ""

# Создание пользователя
if ! id -u unitysphere > /dev/null 2>&1; then
    echo -e "${YELLOW}👤 Создание пользователя unitysphere...${NC}"
    useradd -r -s /bin/bash -d $PROJECT_DIR -m unitysphere
    echo -e "${GREEN}✅ Пользователь создан${NC}"
else
    echo -e "${GREEN}✅ Пользователь unitysphere существует${NC}"
fi

# Создание директории проекта
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}📁 Создание директории проекта...${NC}"
    mkdir -p $PROJECT_DIR
    echo -e "${GREEN}✅ Директория создана${NC}"
fi

# Копирование файлов (если запускается не из проекта)
CURRENT_DIR=$(pwd)
if [ "$CURRENT_DIR" != "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}📦 Текущая директория: $CURRENT_DIR${NC}"
    
    read -p "Скопировать проект в $PROJECT_DIR? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}📋 Копирование файлов...${NC}"
        rsync -av --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' \
              --exclude='.git' --exclude='media' \
              $CURRENT_DIR/ $PROJECT_DIR/
        echo -e "${GREEN}✅ Файлы скопированы${NC}"
    fi
fi

# Установка прав
echo -e "${YELLOW}🔒 Установка прав доступа...${NC}"
chown -R unitysphere:unitysphere $PROJECT_DIR
chmod -R 755 $PROJECT_DIR
if [ -f "$PROJECT_DIR/.env" ]; then
    chmod 600 $PROJECT_DIR/.env
fi
echo -e "${GREEN}✅ Права установлены${NC}"

# Создание директорий для логов
echo -e "${YELLOW}📝 Создание директорий для логов...${NC}"
mkdir -p /var/log/unitysphere
chown unitysphere:unitysphere /var/log/unitysphere
echo -e "${GREEN}✅ Директории созданы${NC}"

# Создание директорий для backups
echo -e "${YELLOW}💾 Создание директорий для backups...${NC}"
mkdir -p /backups/postgres
chown unitysphere:unitysphere /backups/postgres
echo -e "${GREEN}✅ Директории созданы${NC}"

# Копирование service файла
echo -e "${YELLOW}📄 Установка systemd service...${NC}"
if [ -f "systemd/unitysphere-improved.service" ]; then
    cp systemd/unitysphere-improved.service $SERVICE_FILE
    
    # Замена путей в service файле
    sed -i "s|/opt/unitysphere|$PROJECT_DIR|g" $SERVICE_FILE
    
    echo -e "${GREEN}✅ Service файл установлен${NC}"
else
    echo -e "${RED}❌ Файл systemd/unitysphere-improved.service не найден${NC}"
    exit 1
fi

# Reload systemd
echo -e "${YELLOW}🔄 Перезагрузка systemd...${NC}"
systemctl daemon-reload
echo -e "${GREEN}✅ Systemd перезагружен${NC}"

# Enable service
echo -e "${YELLOW}⚡ Включение автозапуска...${NC}"
systemctl enable $SERVICE_NAME.service
echo -e "${GREEN}✅ Автозапуск включен${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Установка завершена!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${YELLOW}📝 Доступные команды:${NC}"
echo ""
echo "   Запуск сервиса:"
echo "   sudo systemctl start $SERVICE_NAME"
echo ""
echo "   Остановка сервиса:"
echo "   sudo systemctl stop $SERVICE_NAME"
echo ""
echo "   Перезапуск сервиса:"
echo "   sudo systemctl restart $SERVICE_NAME"
echo ""
echo "   Статус сервиса:"
echo "   sudo systemctl status $SERVICE_NAME"
echo ""
echo "   Логи сервиса:"
echo "   sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "   Отключить автозапуск:"
echo "   sudo systemctl disable $SERVICE_NAME"
echo ""

read -p "Запустить сервис сейчас? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🚀 Запуск сервиса...${NC}"
    systemctl start $SERVICE_NAME
    
    # Ждем запуска
    sleep 5
    
    # Проверяем статус
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo -e "${GREEN}✅ Сервис запущен успешно!${NC}"
        systemctl status $SERVICE_NAME --no-pager
    else
        echo -e "${RED}❌ Ошибка запуска сервиса${NC}"
        journalctl -u $SERVICE_NAME -n 50 --no-pager
    fi
fi

echo ""
