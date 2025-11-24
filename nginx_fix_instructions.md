# Решение проблемы с Nginx

## Проблема
Сайт fan-club.kz не открывается, потому что Nginx показывает стандартную страницу "Welcome to nginx!" вместо проксирования запросов на Django приложение.

## Причина
В Nginx включен default сайт, который имеет приоритет над нашим сайтом fan-club.kz.

## Решение
Выполните следующие команды с sudo:

```bash
# Остановить Nginx
sudo systemctl stop nginx

# Отключить default сайт
sudo rm /etc/nginx/sites-enabled/default

# Перезапустить Nginx
sudo systemctl start nginx

# Проверить статус
sudo systemctl status nginx
```

## Альтернативное решение (если не хотите удалять default)
Можно отредактировать конфигурацию fan-club.kz и добавить default_server:

```bash
# Отредактировать конфигурацию
sudo nano /etc/nginx/sites-available/fan-club.kz
```

Заменить строку:
```
listen 80;
```

На:
```
listen 80 default_server;
listen [::]:80 default_server;
```

Затем перезагрузить Nginx:
```bash
sudo systemctl reload nginx
```

## Проверка
После выполнения этих команд проверьте:
1. `curl -I http://127.0.0.1` - должен показать Django ответ, а не nginx
2. Откройте в браузере: http://fan-club.kz

## Важно
Убедитесь, что Django сервер работает:
```bash
ps aux | grep "python.*manage.py.*runserver"
```

Если Django не работает, запустите:
```bash
cd /var/www/myapp/eventsite
source venv/bin/activate
python manage.py runserver 127.0.0.1:8000 &
```