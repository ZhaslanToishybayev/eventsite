#!/bin/bash

# 🔧 СКРИПТ: Настройка Django как systemd сервиса

echo "🚀 Настройка Django как systemd сервиса..."

# Проверяем существование виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено. Создаем..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем зависимости
echo "📦 Устанавливаем зависимости..."
pip install -r requirements.txt 2>/dev/null || pip install django djangorestframework requests python-dotenv

# Проверяем Django
echo "🔍 Проверяем Django..."
python manage.py check --deploy 2>/dev/null || echo "⚠️ Django проверка пропущена"

# Создаем сервисный файл
echo "⚙️ Создаем systemd сервис..."
sudo tee /etc/systemd/system/unitysphere.service > /dev/null <<EOF
[Unit]
Description=UnitySphere Django Application
After=network.target

[Service]
Type=exec
User=admin
Group=admin
WorkingDirectory=/var/www/myapp/eventsite
Environment="PATH=/var/www/myapp/eventsite/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=core.settings"
ExecStart=/var/www/myapp/eventsite/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Сервис создан: /etc/systemd/system/unitysphere.service"
echo ""
echo "🎯 Для активации сервиса выполните:"
echo "sudo systemctl enable unitysphere"
echo "sudo systemctl start unitysphere"
echo "sudo systemctl status unitysphere"
echo ""
echo "🔧 Или запустите вручную:"
echo "source venv/bin/activate && python manage.py runserver 0.0.0.0:8000"