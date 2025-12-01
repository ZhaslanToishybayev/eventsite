#!/bin/bash

# 🚀 UnitySphere Update Nginx Config Script
# Обновление nginx конфигурации на порт 8006

echo "🚀 UnitySphere Update Nginx Config Script"
echo "=========================================="
echo ""

# 1. Проверяем, что Django работает на порту 8006
echo "🔍 Проверка Django на порту 8006..."
if curl -s http://127.0.0.1:8006/ > /dev/null 2>&1; then
    echo "✅ Django работает на порту 8006"
else
    echo "❌ Django не работает на порту 8006"
    exit 1
fi

# 2. Создаем резервную копию nginx конфигурации
echo "📁 Создание резервной копии nginx конфигурации..."
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup_$(date +%Y%m%d_%H%M%S)

# 3. Обновляем nginx конфигурацию
echo "🔧 Обновление nginx конфигурации на порт 8006..."
sudo sed -i 's/server 127.0.0.1:8001;/server 127.0.0.1:8006;/' /etc/nginx/nginx.conf
sudo sed -i 's/server 127.0.0.1:8003;/server 127.0.0.1:8006;/' /etc/nginx/nginx.conf

# 4. Проверяем конфигурацию nginx
echo "✅ Проверка nginx конфигурации..."
if sudo nginx -t; then
    echo "✅ Конфигурация nginx валидна"
else
    echo "❌ Ошибка в конфигурации nginx"
    exit 1
fi

# 5. Перезагружаем nginx
echo "🔄 Перезагрузка nginx..."
sudo nginx -s reload

# 6. Ждем 5 секунд
sleep 5

# 7. Проверка сайта
echo "🌐 Проверка сайта через nginx..."
SITE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L http://127.0.0.1/)

if [ "$SITE_STATUS" = "200" ]; then
    echo "✅ Сайт РАБОТАЕТ через nginx!"
    echo ""
    echo "🎉 UnitySphere полностью работает!"
    echo ""
    echo "📊 Финальный статус:"
    echo "   • Django: ✅ Работает на порту 8006"
    echo "   • nginx: ✅ Перенастроен на порт 8006"
    echo "   • Сайт: ✅ Доступен через nginx"
    echo "   • Режим: Minimal (runserver)"
    echo ""
    echo "🛡️ Рекомендуется запустить Auto-Healing:"
    echo "   /var/www/myapp/eventsite/auto_healing.sh"
else
    echo "⚠️ Сайт не работает (код: $SITE_STATUS)"
    echo "💡 Проверьте логи nginx: sudo tail -f /var/log/nginx/error.log"
fi

echo ""
echo "📝 Изменения в nginx:"
echo "   • Upstream Django: 127.0.0.1:8006"
echo "   • Резервная копия: /etc/nginx/nginx.conf.backup_YYYYMMDD_HHMMSS"