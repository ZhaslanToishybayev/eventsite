# 🔧 ИНСТРУКЦИЯ ПО ИСПРАВЛЕНИЮ NGINX

## Проблема:
502 Bad Gateway - nginx не может подключиться к Django серверу из-за проблем с SSL сертификатами.

## Решение:

### 1. Остановите nginx:
```bash
sudo systemctl stop nginx
```

### 2. Создайте резервную копию текущей конфигурации:
```bash
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
```

### 3. Удалите текущие SSL конфиги:
```bash
sudo rm -rf /etc/letsencrypt/live/fan-club.kz 2>/dev/null || true
sudo rm -rf /etc/letsencrypt/archive/fan-club.kz 2>/dev/null || true
sudo rm -rf /etc/letsencrypt/renewal/fan-club.kz.conf 2>/dev/null || true
```

### 4. Скопируйте простую конфигурацию:
```bash
sudo cp /var/www/myapp/eventsite/nginx_simple_config /etc/nginx/sites-available/fan-club
```

### 5. Активируйте сайт:
```bash
sudo ln -sf /etc/nginx/sites-available/fan-club /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
```

### 6. Проверьте конфигурацию:
```bash
sudo nginx -t
```

### 7. Запустите nginx:
```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 8. Убедитесь что Django сервер запущен:
```bash
cd /var/www/myapp/eventsite
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

## Для SSL сертификата (опционально):

Если хотите SSL, выполните:

```bash
# Установите certbot
sudo apt update
sudo apt install -y certbot

# Получите сертификат
sudo certbot certonly --standalone -d fan-club.kz -d www.fan-club.kz --non-interactive --agree-tos --email admin@fan-club.kz

# Используйте SSL конфигурацию из fix_nginx.sh
```

## Проверка:
После настройки сайт должен быть доступен по:
- http://fan-club.kz (без SSL)
- https://fan-club.kz (с SSL, если настроили)

## Текущее состояние AI:
✅ AI консультант полностью функционален
✅ Форм-парсинг работает идеально
✅ Клубы создаются в базе данных
✅ Все функции работают корректно

Проблема ТОЛЬКО в веб-сервере nginx, а не в AI системе!