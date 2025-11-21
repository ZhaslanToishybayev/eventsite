# 🔐 Настройка Google Cloud Console для авторизации

Чтобы кнопка "Войти через Google" заработала, вам нужно получить `Client ID` и `Client Secret` от Google.

## 1. Создание проекта
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/).
2. Создайте новый проект (например, `UnitySphere Auth`).

## 2. Настройка экрана согласия (OAuth Consent Screen)
1. В меню слева выберите **APIs & Services** -> **OAuth consent screen**.
2. Выберите **External** (Внешний) и нажмите **Create**.
3. Заполните обязательные поля:
   - **App name:** UnitySphere
   - **User support email:** ваш email
   - **Developer contact information:** ваш email
4. Нажмите **Save and Continue**.
5. В разделе **Scopes** нажмите **Add or Remove Scopes** и выберите:
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
   - `openid`
6. Нажмите **Update**, затем **Save and Continue**.
7. В разделе **Test Users** добавьте свой email (пока приложение в режиме тестирования).

## 3. Создание ключей (Credentials)
1. В меню слева выберите **Credentials**.
2. Нажмите **Create Credentials** -> **OAuth client ID**.
3. **Application type:** Web application.
4. **Name:** UnitySphere Web Client.
5. **Authorized JavaScript origins:**
   - `http://localhost:8000`
   - `https://fan-club.kz`
   - `https://www.fan-club.kz`
6. **Authorized redirect URIs:**
   - `http://localhost:8000/accounts/google/login/callback/`
   - `https://fan-club.kz/accounts/google/login/callback/`
   - `https://www.fan-club.kz/accounts/google/login/callback/`
7. Нажмите **Create**.
8. **Скопируйте** `Client ID` и `Client Secret`.

## 4. Добавление ключей в Django Admin
1. Зайдите в админку вашего сайта: `http://localhost:8000/admin/` (или на боевом сервере).
2. Найдите раздел **Social Accounts** -> **Social applications**.
3. Нажмите **Add social application**.
4. Заполните форму:
   - **Provider:** Google
   - **Name:** Google Auth
   - **Client id:** (вставьте ваш ID)
   - **Secret key:** (вставьте ваш Secret)
   - **Sites:** Выберите ваш сайт (обычно `example.com` или создайте новый в разделе Sites, если там пусто).
5. Нажмите **Save**.

---

## 🚀 Готово!
Теперь кнопка "Войти через Google" на страницах входа и регистрации будет работать.
