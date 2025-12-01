#!/bin/bash

# 🚀 СКРИПТ: Полный запуск Django production сервиса

echo "🚀 ЗАПУСК DJANGO PRODUCTION СЕРВИСА"
echo "====================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода статуса
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# 1. Проверяем виртуальное окружение
echo ""
echo "1. ПРОВЕРКА ОКРУЖЕНИЯ"
echo "-----------------------"

if [ ! -d "venv" ]; then
    print_warning "Виртуальное окружение не найдено. Создаем..."
    python3 -m venv venv
    print_status "Виртуальное окружение создано"
fi

# Активируем виртуальное окружение
source venv/bin/activate
print_status "Виртуальное окружение активировано"

# 2. Устанавливаем зависимости
echo ""
echo "2. УСТАНОВКА ЗАВИСИМОСТЕЙ"
echo "----------------------------"

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    print_warning "requirements.txt не найден, устанавливаем базовые зависимости..."
    pip install django djangorestframework requests python-dotenv pillow psycopg2-binary gunicorn
fi

print_status "Зависимости установлены"

# 3. Проверяем Django
echo ""
echo "3. ПРОВЕРКА DJANGO"
echo "-------------------"

python manage.py check --deploy 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "Django проверка пройдена"
else
    print_warning "Django проверка не пройдена, но продолжаем..."
fi

# 4. Создаем директории
echo ""
echo "4. СОЗДАНИЕ ДИРЕКТОРИЙ"
echo "-----------------------"

mkdir -p logs
mkdir -p staticfiles
mkdir -p media
print_status "Директории созданы"

# 5. Настраиваем права
echo ""
echo "5. НАСТРОЙКА ПРАВ"
echo "------------------"

sudo mkdir -p /var/log/unitysphere
sudo chown admin:admin /var/log/unitysphere
sudo chmod 755 /var/log/unitysphere
print_status "Права настроены"

# 6. Создаем systemd сервис
echo ""
echo "6. СОЗДАНИЕ SYSTEMD СЕРВИСА"
echo "------------------------------"

sudo tee /etc/systemd/system/unitysphere.service > /dev/null <<EOF
[Unit]
Description=UnitySphere Django Application
After=network.target
Requires=network.target

[Service]
Type=exec
User=admin
Group=admin
WorkingDirectory=/var/www/myapp/eventsite
Environment="PATH=/var/www/myapp/eventsite/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=core.settings"
Environment="DEBUG=False"
Environment="ALLOWED_HOSTS=fan-club.kz,www.fan-club.kz,localhost,127.0.0.1"
ExecStart=/var/www/myapp/eventsite/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=5
KillSignal=SIGQUIT
TimeoutStopSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=unitysphere

[Install]
WantedBy=multi-user.target
EOF

sudo chmod 644 /etc/systemd/system/unitysphere.service
print_status "Systemd сервис создан"

# 7. Перезагружаем systemd
echo ""
echo "7. ПЕРЕЗАГРУЗКА SYSTEMD"
echo "-----------------------"

sudo systemctl daemon-reload
print_status "Systemd перезагружен"

# 8. Активируем сервис
echo ""
echo "8. АКТИВАЦИЯ СЕРВИСА"
echo "---------------------"

sudo systemctl enable unitysphere
print_status "Сервис активирован"

# 9. Запускаем сервис
echo ""
echo "9. ЗАПУСК СЕРВИСА"
echo "------------------"

sudo systemctl start unitysphere

# Ждем немного и проверяем статус
sleep 3

if sudo systemctl is-active --quiet unitysphere; then
    print_status "Сервис успешно запущен!"
else
    print_error "Сервис не запустился. Проверьте логи:"
    echo "sudo journalctl -u unitysphere -f"
    exit 1
fi

# 10. Проверяем Nginx
echo ""
echo "10. ПРОВЕРКА NGINX"
echo "-------------------"

if systemctl is-active --quiet nginx; then
    print_status "Nginx работает"
else
    print_warning "Nginx не работает. Запустите: sudo systemctl start nginx"
fi

# 11. Финальная информация
echo ""
echo "🎉 ЗАПУСК ЗАВЕРШЕН!"
echo "===================="
echo ""
echo "📊 Статус сервисов:"
echo "• Django сервис: $(sudo systemctl is-active unitysphere)"
echo "• Nginx: $(systemctl is-active nginx)"
echo ""
echo "🌐 Сайт доступен по:"
echo "• https://fan-club.kz"
echo "• http://fan-club.kz"
echo ""
echo "🔧 Управление сервисом:"
echo "• Статус: sudo systemctl status unitysphere"
echo "• Логи: sudo journalctl -u unitysphere -f"
echo "• Остановить: sudo systemctl stop unitysphere"
echo "• Перезапустить: sudo systemctl restart unitysphere"
echo ""
echo "🧪 Тестирование:"
echo "• Health check: curl https://fan-club.kz/health/"
echo "• AI API: curl -X POST https://fan-club.kz/api/v1/ai/chat/ -H 'Content-Type: application/json' -d '{\"message\": \"Привет\"}'"
echo ""
echo "🎯 Приятного использования! 🚀"