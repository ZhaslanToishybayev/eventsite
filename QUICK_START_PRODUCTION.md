# 🚀 Quick Start - Production Deployment

**Время на деплой:** ~30 минут  
**Сложность:** Средняя  
**Требуется:** root доступ, Docker, домен

---

## ⚡ Экспресс-деплой (5 шагов)

### Шаг 1: Генерация секретов (2 минуты)

```bash
cd /path/to/unitysphere
python3 scripts/generate_production_secrets.py
```

💾 **Сохраните вывод в безопасное место!**

---

### Шаг 2: Настройка .env (3 минуты)

```bash
nano .env
```

Вставьте:
```bash
# Из вывода generate_production_secrets.py
DJANGO_SECRET_KEY=<сгенерированный-ключ>
DEBUG=False
POSTGRES_PASSWORD=<сгенерированный-пароль>

# Ваши реальные данные
GOOGLE_CLIENT_ID=<из-google-console>
GOOGLE_CLIENT_SECRET=<из-google-console>
OPENAI_API_KEY=<ваш-openai-key>

# Ваш домен
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

---

### Шаг 3: Автоматический деплой (10 минут)

```bash
bash scripts/deploy_production.sh
```

Скрипт автоматически:
- ✅ Создаст backup БД
- ✅ Установит зависимости
- ✅ Применит миграции
- ✅ Соберет статику
- ✅ Перезапустит сервисы
- ✅ Проверит health

---

### Шаг 4: Настройка Google OAuth (2 минуты)

```bash
docker compose exec fnclub python /proj/scripts/setup_google_oauth_production.py
```

Скрипт запросит:
- Домен
- Google Client ID
- Google Client Secret

---

### Шаг 5: Мониторинг и автозапуск (5 минут)

```bash
# Установка мониторинга (cron jobs)
sudo bash scripts/setup_monitoring.sh

# Установка systemd service
sudo bash scripts/setup_systemd_service.sh
```

---

## ✅ Проверка

```bash
# Health check
curl https://your-domain.com/api/v1/ai/health/

# Home page
curl https://your-domain.com/

# Google OAuth
curl -I https://your-domain.com/accounts/google/login/
```

---

## 🎉 Готово!

Ваше приложение в production и работает!

**Что дальше?**
- Мониторьте логи первые 24 часа
- Проверьте бэкапы на следующий день
- Настройте Sentry (опционально)

---

## 📚 Полная документация

- `PRODUCTION_DEPLOYMENT_CHECKLIST.md` - подробный чеклист
- `GOOGLE_OAUTH_SETUP_GUIDE.md` - OAuth инструкция
- `PRODUCTION_READY_SUMMARY.md` - полный обзор
