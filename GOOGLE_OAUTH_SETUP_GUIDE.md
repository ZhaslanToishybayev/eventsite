# 🔐 Подробная инструкция по настройке Google OAuth

## Шаг 1: Создание проекта в Google Cloud Console

### 1.1 Откройте Google Cloud Console
Перейдите: https://console.cloud.google.com/

### 1.2 Создайте новый проект (или используйте существующий)
1. Нажмите на выпадающий список проектов вверху страницы
2. Нажмите "New Project"
3. Введите название: `UnitySphere Production`
4. Нажмите "Create"

---

## Шаг 2: Включение Google+ API

### 2.1 Откройте библиотеку API
1. В меню слева выберите "APIs & Services" → "Library"
2. Найдите "Google+ API" (или "Google People API")
3. Нажмите на API
4. Нажмите "Enable"

---

## Шаг 3: Настройка OAuth Consent Screen

### 3.1 Откройте OAuth consent screen
1. В меню слева: "APIs & Services" → "OAuth consent screen"
2. Выберите тип приложения: **External** (для публичного доступа)
3. Нажмите "Create"

### 3.2 Заполните информацию о приложении

**App information:**
- App name: `UnitySphere`
- User support email: `ваш-email@example.com`
- App logo: (опционально, загрузите логотип 120x120px)

**App domain:**
- Application home page: `https://ваш-домен.com`
- Application privacy policy link: `https://ваш-домен.com/privacy/`
- Application terms of service: `https://ваш-домен.com/terms/`

**Authorized domains:**
Добавьте ваш домен: `ваш-домен.com`

**Developer contact information:**
- Email addresses: `ваш-email@example.com`

Нажмите "Save and Continue"

### 3.3 Scopes (области доступа)
1. Нажмите "Add or Remove Scopes"
2. Выберите следующие scopes:
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
   - `openid`
3. Нажмите "Update"
4. Нажмите "Save and Continue"

### 3.4 Test users (для разработки)
- Если ваше приложение в режиме "Testing", добавьте тестовых пользователей
- Для production переведите в "Production" mode

Нажмите "Save and Continue"

---

## Шаг 4: Создание OAuth Credentials

### 4.1 Создайте OAuth client ID
1. В меню слева: "APIs & Services" → "Credentials"
2. Нажмите "Create Credentials" → "OAuth client ID"
3. Application type: **Web application**
4. Name: `UnitySphere Web Client`

### 4.2 Настройте Authorized JavaScript origins
Добавьте ваши домены:
```
https://ваш-домен.com
https://www.ваш-домен.com
```

**Для локальной разработки также добавьте:**
```
http://localhost:8001
http://127.0.0.1:8001
```

### 4.3 Настройте Authorized redirect URIs
Добавьте callback URL:
```
https://ваш-домен.com/accounts/google/login/callback/
https://www.ваш-домен.com/accounts/google/login/callback/
```

**Для локальной разработки:**
```
http://localhost:8001/accounts/google/login/callback/
```

### 4.4 Создайте credentials
1. Нажмите "Create"
2. **ВАЖНО:** Скопируйте и сохраните:
   - **Client ID** (например: `123456789-abc...xyz.apps.googleusercontent.com`)
   - **Client secret** (например: `GOCSPX-abc...xyz`)

---

## Шаг 5: Настройка в UnitySphere

### 5.1 Обновите .env файл
Откройте `.env` или `.env.production` и добавьте:

```bash
# Google OAuth Production Credentials
GOOGLE_CLIENT_ID=ваш-client-id-из-google-console
GOOGLE_CLIENT_SECRET=ваш-client-secret-из-google-console
PRODUCTION_DOMAIN=ваш-домен.com
```

### 5.2 Запустите скрипт настройки

**Вариант А: Автоматическая настройка (рекомендуется)**
```bash
# Экспортируйте переменные окружения
export GOOGLE_CLIENT_ID="ваш-client-id"
export GOOGLE_CLIENT_SECRET="ваш-client-secret"
export PRODUCTION_DOMAIN="ваш-домен.com"

# Запустите скрипт
docker compose exec fnclub python /proj/scripts/setup_google_oauth_production.py
```

**Вариант Б: Интерактивная настройка**
```bash
# Скрипт запросит данные интерактивно
docker compose exec fnclub python /proj/scripts/setup_google_oauth_production.py
```

**Вариант В: Ручная настройка через Django shell**
```bash
docker compose exec fnclub python /proj/manage.py shell
```

В Django shell:
```python
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# Настройка Site
site = Site.objects.get(id=1)
site.domain = 'ваш-домен.com'
site.name = 'UnitySphere Production'
site.save()

# Настройка Google OAuth
google_app, created = SocialApp.objects.get_or_create(provider='google')
google_app.name = 'Google OAuth'
google_app.client_id = 'ваш-client-id'
google_app.secret = 'ваш-client-secret'
google_app.save()
google_app.sites.add(site)

print("✅ Настройка завершена!")
```

---

## Шаг 6: Проверка настройки

### 6.1 Проверьте в Django Admin
1. Откройте: `https://ваш-домен.com/admin/`
2. Логин с superuser
3. Перейдите: "Sites" → "Sites"
4. Проверьте что domain = `ваш-домен.com`
5. Перейдите: "Social applications"
6. Проверьте что Google app настроен и связан с вашим site

### 6.2 Тестирование OAuth потока
1. Откройте браузер в режиме инкогнито
2. Перейдите: `https://ваш-домен.com/accounts/google/login/`
3. Должен произойти редирект на Google
4. Авторизуйтесь через Google аккаунт
5. Должен произойти редирект обратно на ваш сайт
6. Пользователь должен быть создан и залогинен

### 6.3 Проверьте в базе данных
```bash
docker compose exec fnclub python /proj/manage.py shell
```

```python
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model

User = get_user_model()

# Проверка пользователей с Google аккаунтами
google_users = SocialAccount.objects.filter(provider='google')
print(f"Пользователей с Google: {google_users.count()}")

for social_account in google_users:
    print(f"- {social_account.user.email} (Google UID: {social_account.uid})")
```

---

## Шаг 7: Troubleshooting (Решение проблем)

### Проблема: Redirect URI mismatch
**Ошибка:** `Error 400: redirect_uri_mismatch`

**Решение:**
1. Убедитесь что в Google Console добавлен точный URL:
   - `https://ваш-домен.com/accounts/google/login/callback/`
2. Проверьте что нет лишних слешей или пробелов
3. Проверьте что домен в Django Site совпадает с реальным

### Проблема: Site matching query does not exist
**Ошибка:** `Site matching query does not exist`

**Решение:**
```python
from django.contrib.sites.models import Site
site = Site.objects.create(id=1, domain='ваш-домен.com', name='UnitySphere')
```

### Проблема: Social account already exists
**Ошибка:** User с таким email уже существует

**Решение:**
1. В Django settings добавьте:
```python
SOCIALACCOUNT_AUTO_SIGNUP = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
```

2. Или свяжите аккаунты вручную в админке

### Проблема: Access denied
**Ошибка:** OAuth consent screen не прошел review

**Решение:**
1. Для тестирования: добавьте email в Test users
2. Для production: submit app for verification в Google Console

---

## Шаг 8: Production Checklist

После настройки проверьте:

- [ ] Client ID и Secret правильно настроены в .env
- [ ] Domain в Django Site совпадает с production доменом
- [ ] Authorized redirect URIs включают production URL
- [ ] OAuth consent screen заполнен полностью
- [ ] Privacy Policy и Terms доступны по указанным URL
- [ ] SSL сертификат установлен (HTTPS работает)
- [ ] Тестовый вход через Google работает
- [ ] Пользователь создается автоматически
- [ ] Email пользователя сохраняется правильно

---

## Шаг 9: Безопасность

### 9.1 Защита credentials
```bash
# НЕ коммитьте в Git!
echo ".env.production" >> .gitignore
echo "*.secret" >> .gitignore

# Права доступа только для owner
chmod 600 .env.production
```

### 9.2 Ротация секретов
Периодически обновляйте Client Secret:
1. В Google Console создайте новый Client Secret
2. Обновите в .env
3. Перезапустите приложение
4. Удалите старый secret из Google Console

### 9.3 Мониторинг
Следите за:
- Количеством неудачных попыток входа
- Подозрительными redirect URLs
- OAuth error logs

---

## Дополнительные ресурсы

- **Google OAuth Documentation:** https://developers.google.com/identity/protocols/oauth2
- **Django Allauth Documentation:** https://django-allauth.readthedocs.io/
- **Google Cloud Console:** https://console.cloud.google.com/

---

## Поддержка

Если возникли проблемы:
1. Проверьте логи: `docker compose logs fnclub | grep -i oauth`
2. Проверьте Django admin: Sites и Social applications
3. Проверьте настройки в Google Console

---

**Последнее обновление:** 2025-11-21
