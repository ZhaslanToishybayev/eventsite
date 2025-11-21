# ✅ Production Deployment Checklist для UnitySphere

**Версия:** 1.0  
**Дата:** 2025-11-21  
**Статус:** Готово к использованию

---

## 📋 Pre-Deployment Checklist

### 1. Безопасность (Critical) 🔐

- [ ] Сгенерированы новые секретные ключи
  ```bash
  python3 scripts/generate_production_secrets.py
  ```

- [ ] Обновлен `.env` файл с production значениями
  - [ ] `DEBUG=False`
  - [ ] `DJANGO_SECRET_KEY` (новый сильный ключ)
  - [ ] `POSTGRES_PASSWORD` (сильный пароль)
  - [ ] `ALLOWED_HOSTS` (ваш домен)
  - [ ] `CSRF_TRUSTED_ORIGINS` (ваш домен)

- [ ] Настроены Google OAuth credentials
  - [ ] Получены credentials из Google Cloud Console
  - [ ] Обновлены `GOOGLE_CLIENT_ID` и `GOOGLE_CLIENT_SECRET`
  - [ ] Запущен скрипт `scripts/setup_google_oauth_production.py`

- [ ] Настроен OpenAI API ключ
  - [ ] Production API key добавлен в `.env`
  - [ ] Проверены лимиты и биллинг

- [ ] Проверены права доступа к файлам
  ```bash
  chmod 600 .env
  chmod 755 scripts/*.sh
  ```

---

### 2. Инфраструктура 🏗️

- [ ] Сервер подготовлен
  - [ ] Ubuntu 20.04/22.04 или аналог
  - [ ] Минимум 2GB RAM, 2 CPU cores
  - [ ] Минимум 20GB свободного места
  - [ ] Docker и Docker Compose установлены

- [ ] Настроен firewall
  ```bash
  sudo ufw allow 22/tcp   # SSH
  sudo ufw allow 80/tcp   # HTTP
  sudo ufw allow 443/tcp  # HTTPS
  sudo ufw enable
  ```

- [ ] Домен настроен
  - [ ] DNS A-запись указывает на сервер
  - [ ] DNS CNAME для www (опционально)
  - [ ] TTL снижен перед переключением

- [ ] SSL сертификат получен
  ```bash
  sudo certbot --nginx -d your-domain.com -d www.your-domain.com
  ```

- [ ] Nginx настроен как reverse proxy
  - [ ] Конфигурация скопирована из `nginx/unitysphere.conf`
  - [ ] Протестирована: `sudo nginx -t`
  - [ ] Перезагружен: `sudo systemctl reload nginx`

---

### 3. База данных 💾

- [ ] PostgreSQL настроен
  - [ ] Версия 16 (в Docker)
  - [ ] Persistent volume для данных
  - [ ] Сильный пароль установлен

- [ ] Создан план бэкапов
  - [ ] Скрипт `scripts/backup_database.sh` протестирован
  - [ ] Cron job настроен (ежедневно в 2:00)
  - [ ] Директория `/backups/postgres` создана
  - [ ] Retention policy: 30 дней

- [ ] Протестировано восстановление
  ```bash
  bash scripts/backup_database.sh
  bash scripts/restore_database.sh /backups/postgres/latest.sql.gz
  ```

---

### 4. Приложение 🚀

- [ ] Код развернут на сервере
  ```bash
  git clone your-repo.git /opt/unitysphere
  cd /opt/unitysphere
  ```

- [ ] Зависимости установлены
  ```bash
  docker compose build
  ```

- [ ] Миграции применены
  ```bash
  docker compose exec fnclub python /proj/manage.py migrate
  ```

- [ ] Статические файлы собраны
  ```bash
  docker compose exec fnclub python /proj/manage.py collectstatic --noinput
  ```

- [ ] Создан superuser
  ```bash
  docker compose exec fnclub python /proj/manage.py createsuperuser
  ```

- [ ] Настроен Django Site
  ```bash
  docker compose exec fnclub python /proj/scripts/setup_google_oauth_production.py
  ```

---

### 5. Мониторинг и логи 📊

- [ ] Директории для логов созданы
  ```bash
  sudo mkdir -p /var/log/unitysphere
  sudo chown unitysphere:unitysphere /var/log/unitysphere
  ```

- [ ] Health check скрипт протестирован
  ```bash
  bash scripts/health_check.sh
  ```

- [ ] Мониторинг настроен
  ```bash
  sudo bash scripts/setup_monitoring.sh
  ```

- [ ] Cron jobs проверены
  ```bash
  crontab -l
  ```

- [ ] Logrotate настроен
  - [ ] Конфигурация в `/etc/logrotate.d/unitysphere`
  - [ ] Протестирован: `sudo logrotate -d /etc/logrotate.d/unitysphere`

- [ ] (Опционально) Sentry настроен
  - [ ] `SENTRY_DSN` добавлен в `.env`
  - [ ] Тестовое событие отправлено

---

### 6. Автозапуск 🔄

- [ ] Systemd service установлен
  ```bash
  sudo bash scripts/setup_systemd_service.sh
  ```

- [ ] Service включен
  ```bash
  sudo systemctl enable unitysphere
  sudo systemctl start unitysphere
  ```

- [ ] Автозапуск протестирован
  ```bash
  sudo systemctl status unitysphere
  sudo reboot
  # После перезагрузки проверить
  sudo systemctl status unitysphere
  ```

---

## 🚀 Deployment Steps

### Шаг 1: Предварительная подготовка

```bash
# На локальной машине
cd /path/to/unitysphere

# Генерация секретов
python3 scripts/generate_production_secrets.py > production_secrets.txt

# Сохраните production_secrets.txt в безопасном месте!
```

### Шаг 2: Настройка сервера

```bash
# На production сервере
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Создание пользователя
sudo useradd -r -s /bin/bash -d /opt/unitysphere -m unitysphere
sudo usermod -aG docker unitysphere
```

### Шаг 3: Развертывание кода

```bash
# Клонирование репозитория
sudo -u unitysphere git clone your-repo.git /opt/unitysphere
cd /opt/unitysphere

# Создание .env файла
sudo -u unitysphere nano .env
# Вставьте production конфигурацию из production_secrets.txt

# Права доступа
sudo chmod 600 .env
sudo chown unitysphere:unitysphere .env
```

### Шаг 4: Запуск приложения

```bash
# Использование автоматического скрипта деплоя
sudo -u unitysphere bash scripts/deploy_production.sh
```

**ИЛИ вручную:**

```bash
# Сборка и запуск
docker compose build
docker compose up -d

# Миграции
docker compose exec fnclub python /proj/manage.py migrate

# Статика
docker compose exec fnclub python /proj/manage.py collectstatic --noinput

# Superuser
docker compose exec fnclub python /proj/manage.py createsuperuser

# Google OAuth
docker compose exec fnclub python /proj/scripts/setup_google_oauth_production.py
```

### Шаг 5: Настройка мониторинга

```bash
# Установка мониторинга
sudo bash scripts/setup_monitoring.sh

# Установка systemd service
sudo bash scripts/setup_systemd_service.sh
```

### Шаг 6: Настройка Nginx

```bash
# Копирование конфигурации
sudo cp nginx/unitysphere.conf /etc/nginx/sites-available/unitysphere

# Обновите домен в конфигурации
sudo nano /etc/nginx/sites-available/unitysphere

# Включение сайта
sudo ln -s /etc/nginx/sites-available/unitysphere /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Шаг 7: Получение SSL сертификата

```bash
# Установка certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Проверка авто-обновления
sudo certbot renew --dry-run
```

---

## ✅ Post-Deployment Verification

### Immediate Checks (сразу после деплоя)

```bash
# 1. Проверка Docker контейнеров
docker compose ps
# Должны быть: fnclub (Up), fnclub-db (Up)

# 2. Health check
curl https://your-domain.com/api/v1/ai/health/
# Должен вернуть: {"overall_status":"healthy",...}

# 3. Проверка главной страницы
curl -I https://your-domain.com/
# Должен вернуть: HTTP/2 200

# 4. Проверка admin панели
curl -I https://your-domain.com/admin/
# Должен вернуть: HTTP/2 200 или 302

# 5. Проверка статических файлов
curl -I https://your-domain.com/static/css/ai-chat-widget.css
# Должен вернуть: HTTP/2 200

# 6. Проверка Google OAuth
curl -I https://your-domain.com/accounts/google/login/
# Должен вернуть: HTTP/2 302 (redirect)
```

### Database Checks

```bash
# Подключение к БД
docker compose exec fnclub-db psql -U postgres -d postgres

# В psql:
\dt                          # Список таблиц
SELECT COUNT(*) FROM accounts_user;
SELECT COUNT(*) FROM clubs_club;
\q
```

### Log Checks

```bash
# Проверка логов приложения
docker compose logs --tail 100 fnclub

# Проверка логов базы данных
docker compose logs --tail 50 fnclub-db

# Проверка системных логов
sudo journalctl -u unitysphere -n 50
```

---

## 📈 First 24 Hours Monitoring

### Что отслеживать:

1. **Ошибки в логах**
   ```bash
   docker compose logs -f fnclub | grep -i error
   ```

2. **Использование ресурсов**
   ```bash
   docker stats
   htop
   ```

3. **Количество пользователей**
   ```bash
   watch -n 60 'docker compose exec -T fnclub-db psql -U postgres -d postgres -t -c "SELECT COUNT(*) FROM accounts_user;"'
   ```

4. **Health checks**
   ```bash
   watch -n 300 'curl -s https://your-domain.com/api/v1/ai/health/ | jq'
   ```

5. **OpenAI API usage**
   - Проверяйте в OpenAI Dashboard
   - Мониторьте costs

---

## 🔧 Common Issues & Solutions

### Issue 1: Static files не загружаются

**Solution:**
```bash
docker compose exec fnclub python /proj/manage.py collectstatic --noinput
sudo systemctl reload nginx
```

### Issue 2: Database connection error

**Solution:**
```bash
# Проверка что БД работает
docker compose ps fnclub-db
docker compose restart fnclub-db
docker compose restart fnclub
```

### Issue 3: Google OAuth не работает

**Solution:**
```bash
# Проверка Site в Django admin
docker compose exec fnclub python /proj/manage.py shell
>>> from django.contrib.sites.models import Site
>>> site = Site.objects.get(id=1)
>>> print(site.domain)  # Должен быть ваш домен
>>> site.domain = 'your-domain.com'
>>> site.save()
```

### Issue 4: 502 Bad Gateway

**Solution:**
```bash
# Проверка что приложение запущено
docker compose ps
docker compose up -d

# Проверка Nginx
sudo nginx -t
sudo systemctl status nginx
```

---

## 📞 Emergency Contacts

- **DevOps Team:** [контакты]
- **On-Call Engineer:** [контакты]
- **Database Admin:** [контакты]

---

## 🎯 Success Criteria

Деплой считается успешным если:

- ✅ Все Docker контейнеры работают
- ✅ Health check возвращает "healthy"
- ✅ Главная страница загружается < 1 секунды
- ✅ Admin панель доступна
- ✅ Google OAuth работает
- ✅ AI consultant отвечает на запросы
- ✅ Нет критических ошибок в логах
- ✅ SSL сертификат действителен
- ✅ Бэкапы создаются автоматически
- ✅ Мониторинг работает

---

**Последнее обновление:** 2025-11-21  
**Подготовлено:** Автоматизированной системой подготовки к production
