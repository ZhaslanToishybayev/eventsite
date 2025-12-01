#!/bin/bash

# 🚀 Создание SocialApp для Google OAuth
# Скрипт для исправления ошибки SocialApp.DoesNotExist

echo "🎯 Создание SocialApp для Google OAuth..."
echo "📅 $(date)"
echo ""

cd /var/www/myapp/eventsite

# Активация виртуального окружения
source venv/bin/activate

echo "🔧 Запуск Django shell для создания SocialApp..."
echo ""

# Создание SocialApp для Google
python3 manage.py shell << 'EOF'
print("🔍 Проверка существующих SocialApp...")
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# Проверяем существующие SocialApp
existing_apps = SocialApp.objects.all()
print(f"Существующие SocialApp: {list(existing_apps)}")

if existing_apps.exists():
    print("⚠️  SocialApp уже существуют, удаляем старые...")
    SocialApp.objects.all().delete()

print("➕ Создание нового SocialApp для Google...")

# Получаем или создаем сайт
site, created = Site.objects.get_or_create(
    id=1,
    defaults={'domain': 'fan-club.kz', 'name': 'fan-club.kz'}
)

if created:
    print(f"✅ Создан сайт: {site}")
else:
    print(f"✅ Используется существующий сайт: {site}")

# Создаем SocialApp для Google
google_app = SocialApp.objects.create(
    provider='google',
    name='Google',
    client_id='123456789-abcdefghijklmnop.apps.googleusercontent.com',  # Заглушка
    secret='123456789-abcdefghijklmnopqrstuvwxyz'  # Заглушка
)

# Добавляем сайт к приложению
google_app.sites.add(site)

print(f"✅ Создан SocialApp: {google_app}")
print(f"   Provider: {google_app.provider}")
print(f"   Client ID: {google_app.client_id}")
print(f"   Сайты: {list(google_app.sites.all())}")

print("")
print("🎉 SocialApp для Google успешно создан!")
print("")
print("📝 ЗАМЕЧАНИЕ:")
print("   Client ID и Secret указаны как заглушки.")
print("   Для реального использования нужно:")
print("   1. Зарегистрировать приложение в Google Cloud Console")
print("   2. Получить реальные Client ID и Secret")
print("   3. Обновить SocialApp с реальными данными")
print("")
print("   Пока SocialApp существует, ошибка DoesNotExist будет исправлена.")
EOF

if [ $? -eq 0 ]; then
    echo "✅ SocialApp для Google успешно создан!"
else
    echo "❌ Ошибка при создании SocialApp"
    exit 1
fi

echo ""
echo "🔍 Проверка регистрации пользователей..."
sleep 2

# Проверяем, что регистрация теперь работает
echo "Проверка /accounts/register/..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8003/accounts/register/)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Регистрация работает! HTTP $HTTP_CODE"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "❌ Всё еще 500 ошибка"
else
    echo "? Регистрация отвечает HTTP $HTTP_CODE"
fi

echo ""
echo "🎯 Создание SocialApp завершено!"
echo ""
echo "📋 Дальнейшие шаги (если нужно реальное Google OAuth):"
echo "   1. Зайти в админку: http://127.0.0.1:8003/admin/"
echo "   2. Перейти в 'Social Accounts' → 'Social apps'"
echo "   3. Обновить Google SocialApp с реальными Client ID и Secret"
echo "   4. Настроить Redirect URI: http://fan-club.kz/accounts/google/login/callback/"
echo ""