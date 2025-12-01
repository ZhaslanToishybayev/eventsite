#!/bin/bash

# 🚀 Обновление SocialApp для Google OAuth с реальными данными
# Скрипт для замены заглушечных данных на реальные Google OAuth credentials

echo "🎯 Обновление SocialApp для Google OAuth с реальными данными..."
echo "📅 $(date)"
echo ""

cd /var/www/myapp/eventsite

# Активация виртуального окружения
source venv/bin/activate

echo "🔧 Запуск Django shell для обновления SocialApp..."
echo ""

# Обновление SocialApp с реальными данными
python3 manage.py shell << 'EOF'
print("🔍 Поиск существующего SocialApp для Google...")
from allauth.socialaccount.models import SocialApp

try:
    # Ищем существующий Google SocialApp
    google_app = SocialApp.objects.get(provider='google')
    print(f"✅ Найден SocialApp: {google_app}")

    # Обновляем с реальными данными
    google_app.client_id = '218112463828-ak1b84bokemb0o3r40m0pnvvvkst70n6.apps.googleusercontent.com'
    google_app.secret = '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'
    google_app.save()

    print(f"✅ SocialApp обновлен с реальными данными!")
    print(f"   Provider: {google_app.provider}")
    print(f"   Client ID: {google_app.client_id}")
    print(f"   Secret: {'*' * len(google_app.secret)}")  # Скрываем секрет в выводе

    # Проверяем, что все сохранено
    updated_app = SocialApp.objects.get(provider='google')
    print(f"✅ Проверка: {updated_app} - данные сохранены")

except SocialApp.DoesNotExist:
    print("❌ SocialApp для Google не найден")
    print("   Создайте SocialApp вручную через админку:")
    print("   /admin/socialaccount/socialapp/add/")
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("")
print("🎉 SocialApp для Google успешно обновлен!")
print("")
print("📋 Настройки Google OAuth:")
print("   Client ID: 218112463828-ak1b84bokemb0o3r40m0pnvvvkst70n6.apps.googleusercontent.com")
print("   Redirect URI: http://fan-club.kz/accounts/google/login/callback/")
print("")
print("⚠️  ВАЖНО:")
print("   1. Убедитесь, что в Google Cloud Console добавлен Redirect URI")
print("   2. Redirect URI должен быть: http://fan-club.kz/accounts/google/login/callback/")
print("   3. Если используете HTTPS, укажите: https://fan-club.kz/accounts/google/login/callback/")
print("")
EOF

if [ $? -eq 0 ]; then
    echo "✅ SocialApp для Google успешно обновлен!"
else
    echo "❌ Ошибка при обновлении SocialApp"
    exit 1
fi

echo ""
echo "🔍 Проверка Google OAuth..."
sleep 2

# Проверяем, что Google OAuth теперь работает с реальными данными
echo "Проверка /accounts/google/login/..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8003/accounts/google/login/)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Google OAuth работает! HTTP $HTTP_CODE"
    echo "   Пользователи могут входить через Google"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "❌ Ошибка сервера при Google OAuth"
    echo "   Проверьте настройки в Google Cloud Console"
else
    echo "? Google OAuth отвечает HTTP $HTTP_CODE"
fi

echo ""
echo "🎯 Обновление SocialApp завершено!"
echo ""
echo "📋 Дальнейшие шаги:"
echo "   1. Проверьте Redirect URI в Google Cloud Console"
echo "   2. Протестируйте вход через Google на сайте"
echo "   3. При необходимости настройте HTTPS в Redirect URI"
echo ""