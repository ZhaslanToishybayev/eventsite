#!/bin/bash

# 🚀 UnitySphere Update Nginx Config
# Обновление nginx конфигурации на порт 8006

echo "🚀 Обновление nginx конфигурации на порт 8006..."

# 1. Обновляем конфигурацию
sudo sed -i 's/server 127.0.0.1:8001;/server 127.0.0.1:8006;/' /etc/nginx/nginx.conf
sudo sed -i 's/server 127.0.0.1:8003;/server 127.0.0.1:8006;/' /etc/nginx/nginx.conf

# 2. Проверяем конфигурацию
if sudo nginx -t; then
    echo "✅ Конфигурация nginx валидна"

    # 3. Перезагружаем nginx
    sudo nginx -s reload
    echo "✅ nginx перезагружен"

    # 4. Проверяем сайт
    sleep 3
    SITE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L http://127.0.0.1/)

    if [ "$SITE_STATUS" = "200" ]; then
        echo "✅ Сайт РАБОТАЕТ!"
    else
        echo "⚠️ Сайт не работает (код: $SITE_STATUS)"
    fi
else
    echo "❌ Ошибка в конфигурации nginx"
fi