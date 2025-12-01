#!/bin/bash

# 🔧 СКРИПТ: Автоматическая настройка Django production сервиса

echo "🚀 Настройка Django production сервиса..."

# Проверяем и создаем виртуальное окружение
echo "🐍 Проверяем виртуальное окружение..."
if [ ! -d "venv" ]; then
    echo "📦 Создаем виртуальное окружение..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем зависимости
echo "📦 Устанавливаем зависимости..."
pip install -r requirements.txt 2>/dev/null || {
    echo "⚠️ requirements.txt не найден, устанавливаем базовые зависимости..."
    pip install django djangorestframework requests python-dotenv pillow
}

# Проверяем Django
echo "🔍 Проверяем Django..."
python manage.py check --deploy 2>/dev/null || {
    echo "⚠️ Django проверка не пройдена, но продолжаем..."
}

# Создаем директорию для логов
echo "📁 Создаем директорию для логов..."
sudo mkdir -p /var/log/unitysphere
sudo chown admin:admin /var/log/unitysphere

# Создаем systemd сервис
echo "⚙️ Создаем systemd сервис..."
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

echo "✅ Сервис создан: /etc/systemd/system/unitysphere.service"

# Перезагружаем systemd
echo "🔄 Перезагружаем systemd..."
sudo systemctl daemon-reload

# Даем права на файл сервиса
sudo chmod 644 /etc/systemd/system/unitysphere.service

echo ""
echo "🎯 Следующие шаги:"
echo "==================="
echo "1. Активировать сервис:"
echo "   sudo systemctl enable unitysphere"
echo ""
echo "2. Запустить сервис:"
echo "   sudo systemctl start unitysphere"
echo ""
echo "3. Проверить статус:"
echo "   sudo systemctl status unitysphere"
echo ""
echo "4. Просмотреть логи:"
echo "   sudo journalctl -u unitysphere -f"
echo ""
echo "5. Или запустить вручную для тестирования:"
echo "   source venv/bin/activate && python manage.py runserver 0.0.0.0:8000"
echo ""

# Проверяем, работает ли Nginx
echo "🔍 Проверяем Nginx..."
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx работает"
else
    echo "⚠️ Nginx не работает. Запустите: sudo systemctl start nginx"
fi

echo ""
echo "🎯 После запуска сервиса, сайт должен быть доступен по:"
echo "   https://fan-club.kz"
echo "   http://fan-club.kz"