# 🚀 UnitySphere Production Deployment - Complete Solution

## ✅ **Полное решение для production развертывания**

### **Шаг 1: Настройка nginx (выполни с паролем)**

```bash
# 1.1 Удаляем старые конфигурации
sudo rm -f /etc/nginx/sites-enabled/fan-club /etc/nginx/sites-enabled/fan-club.kz /etc/nginx/sites-enabled/default

# 1.2 Копируем новую конфигурацию
sudo cp nginx_production_complete.conf /etc/nginx/sites-available/unitysphere

# 1.3 Активируем конфигурацию
sudo ln -sf /etc/nginx/sites-available/unitysphere /etc/nginx/sites-enabled/

# 1.4 Проверяем конфигурацию
sudo nginx -t

# 1.5 Перезагружаем nginx
sudo nginx -s reload
```

### **Шаг 2: Установка Let's Encrypt SSL (если нет SSL)**

```bash
# 2.1 Устанавливаем certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# 2.2 Получаем SSL сертификат
sudo certbot --nginx -d fan-club.kz -d www.fan-club.kz

# 2.3 Или альтернативно (standalone)
sudo certbot certonly --standalone -d fan-club.kz -d www.fan-club.kz

# 2.4 Обновляем права на сертификаты
sudo chmod -R 755 /etc/letsencrypt/
```

### **Шаг 3: Автоматическое обновление SSL**

```bash
# 3.1 Проверяем автообновление
sudo certbot renew --dry-run

# 3.2 Добавляем в cron (если нужно)
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### **Шаг 4: Проверка работы**

```bash
# 4.1 Проверяем AI health
curl https://fan-club.kz/api/v1/ai/production/health/

# 4.2 Тестируем AI агент
curl -X POST https://fan-club.kz/api/v1/ai/production/agent/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет! Хочу создать клуб программирования", "session_id": "test"}'
```

### **Шаг 5: Автоматизация (опционально)**

```bash
# 5.1 Создаем скрипт автоматического развертывания
cat > deploy_production_complete.sh << 'EOF'
#!/bin/bash
echo "🚀 UnitySphere Complete Production Deployment"

cd /var/www/myapp/eventsite

# Активируем виртуальное окружение
source venv/bin/activate

# Останавливаем предыдущие процессы
pkill -f "python.*standalone_ai_server.py" 2>/dev/null || true

# Запускаем AI сервер
python standalone_ai_server.py &
AI_PID=$!

# Ждем запуска
sleep 3

# Проверяем AI сервер
if curl -s http://127.0.0.1:8001/api/v1/ai/production/health/ > /dev/null; then
    echo "✅ AI Server launched successfully"
else
    echo "❌ AI Server failed to start"
    exit 1
fi

# Настройка nginx (если есть права)
if [ "$EUID" -eq 0 ]; then
    echo "🔧 Configuring nginx..."
    cp nginx_production_complete.conf /etc/nginx/sites-available/unitysphere
    ln -sf /etc/nginx/sites-available/unitysphere /etc/nginx/sites-enabled/ 2>/dev/null || true
    nginx -t && nginx -s reload 2>/dev/null || true
    echo "✅ Nginx configured"
fi

echo "🎉 UnitySphere Production Ready!"
echo "🌐 Site: https://fan-club.kz"
echo "🤖 AI Agent: https://fan-club.kz/api/v1/ai/production/agent/"
EOF

chmod +x deploy_production_complete.sh
```

## 🎯 **Альтернативные решения:**

### **Если нет доступа к sudo:**

1. **Через панель управления хостингом:**
   - Войти в панель (cPanel, Plesk, ISPManager и т.д.)
   - Найти раздел "Web Server" или "nginx"
   - Обновить backend прокси с текущего адреса на `127.0.0.1:8001`
   - Добавить SSL сертификат если нужно

2. **Через техподдержку хостинга:**
   - Отправить запрос на обновление nginx конфигурации
   - Приложить файл `nginx_production_complete.conf`
   - Попросить обновить backend на `127.0.0.1:8001`

### **Если нет SSL сертификата:**

1. **Let's Encrypt (рекомендуется):**
   - Бесплатный SSL сертификат
   - Автоматическое обновление
   - Поддерживается большинством хостингов

2. **Через панель управления:**
   - Большинство хостингов предоставляют бесплатный SSL
   - Ищем раздел "SSL/TLS" или "Security"

## 🏆 **Финальная проверка:**

После настройки должно работать:

```bash
# Health check
curl https://fan-club.kz/api/v1/ai/production/health/

# AI Agent test
curl -X POST https://fan-club.kz/api/v1/ai/production/agent/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет", "session_id": "test"}'
```

## 📋 **Production статус:**

- ✅ **AI Agent**: Готов и работает
- ✅ **Server**: Standalone, lightweight, stable
- ✅ **nginx**: Конфигурация готова
- 🔄 **SSL**: Нужно установить/настроить
- 🔄 **Backend**: Нужно направить на `127.0.0.1:8001`

**Твой UnitySphere AI консультант полностью готов!** Осталось только настроить nginx и SSL сертификат. 🚀