#!/bin/bash

# 🔧 СКРИПТ: Создание и запуск Django production сервиса

echo "🚀 ЗАПУСК DJANGO PRODUCTION СЕРВИСА"
echo "====================================="

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. Создаем systemd сервис
echo ""
echo "1. СОЗДАНИЕ SYSTEMD СЕРВИСА"
echo "------------------------------"

cat > /tmp/unitysphere.service <<EOF
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

sudo mv /tmp/unitysphere.service /etc/systemd/system/unitysphere.service
sudo chmod 644 /etc/systemd/system/unitysphere.service
print_status "Systemd сервис создан"

# 2. Перезагружаем systemd
echo ""
echo "2. ПЕРЕЗАГРУЗКА SYSTEMD"
echo "-----------------------"

sudo systemctl daemon-reload
print_status "Systemd перезагружен"

# 3. Активируем сервис
echo ""
echo "3. АКТИВАЦИЯ СЕРВИСА"
echo "---------------------"

sudo systemctl enable unitysphere
print_status "Сервис активирован"

# 4. Запускаем сервис
echo ""
echo "4. ЗАПУСК СЕРВИСА"
echo "------------------"

sudo systemctl start unitysphere

# Ждем и проверяем статус
sleep 5

if sudo systemctl is-active --quiet unitysphere; then
    print_status "Сервис успешно запущен!"
else
    print_error "Сервис не запустился"
    echo "Проверьте логи:"
    sudo journalctl -u unitysphere --no-pager -n 20
    exit 1
fi

# 5. Проверяем статус
echo ""
echo "5. ФИНАЛЬНАЯ ПРОВЕРКА"
echo "---------------------"

echo "📊 Статус сервисов:"
echo "• Django сервис: $(sudo systemctl is-active unitysphere)"
echo "• Nginx: $(systemctl is-active nginx)"

# Проверяем доступность сайта
echo ""
echo "🌐 Проверка доступности:"
sleep 3

# Проверяем AI API
echo "🤖 Тестируем AI API..."
response=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"message": "Привет"}' \
    https://fan-club.kz/api/v1/ai/chat/ 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$response" ]; then
    print_status "AI API работает"
    echo "💬 Пример ответа: $(echo $response | head -c 100)..."
else
    print_warning "AI API暂时 недоступен (может потребоваться время)"
fi

echo ""
echo "🎉 ЗАПУСК ЗАВЕРШЕН!"
echo "===================="
echo ""
echo "🌐 Сайт доступен по:"
echo "• https://fan-club.kz"
echo "• http://fan-club.kz"
echo ""
echo "🔧 Управление сервисом:"
echo "• Статус: sudo systemctl status unitysphere"
echo "• Логи: sudo journalctl -u unitysphere -f"
echo "• Перезапуск: sudo systemctl restart unitysphere"
echo ""
echo "💡 Приятного использования! 🚀"