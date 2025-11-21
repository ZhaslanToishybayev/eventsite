#!/usr/bin/env python3
"""
Скрипт настройки Google OAuth для production окружения
Использование: 
  docker compose exec fnclub python /proj/scripts/setup_google_oauth_production.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/proj')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

def setup_google_oauth():
    """Настройка Google OAuth для production"""
    
    print("=" * 60)
    print("🔐 Настройка Google OAuth для Production")
    print("=" * 60)
    print()
    
    # Получаем данные из environment или запрашиваем у пользователя
    domain = os.getenv('PRODUCTION_DOMAIN')
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not domain:
        print("📝 Введите домен вашего production сервера:")
        print("   Примеры: fan-club.kz, www.unitysphere.com")
        domain = input("   Домен: ").strip()
        if not domain:
            print("❌ Ошибка: Домен обязателен!")
            return False
    
    if not google_client_id:
        print()
        print("📝 Введите Google Client ID:")
        print("   (Получить можно в Google Cloud Console)")
        google_client_id = input("   Client ID: ").strip()
        if not google_client_id:
            print("❌ Ошибка: Client ID обязателен!")
            return False
    
    if not google_client_secret:
        print()
        print("📝 Введите Google Client Secret:")
        google_client_secret = input("   Client Secret: ").strip()
        if not google_client_secret:
            print("❌ Ошибка: Client Secret обязателен!")
            return False
    
    print()
    print("=" * 60)
    print("📋 Конфигурация:")
    print("=" * 60)
    print(f"   Домен: {domain}")
    print(f"   Client ID: {google_client_id[:20]}...")
    print(f"   Client Secret: {'*' * 20}")
    print()
    
    confirm = input("Продолжить? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Отменено")
        return False
    
    print()
    print("🔧 Настройка Django Site...")
    
    # Настраиваем Site
    site, created = Site.objects.get_or_create(id=1)
    site.domain = domain
    site.name = f'UnitySphere ({domain})'
    site.save()
    
    if created:
        print(f"✅ Site создан: {site.domain}")
    else:
        print(f"✅ Site обновлен: {site.domain}")
    
    print()
    print("🔧 Настройка Google Social App...")
    
    # Настраиваем Google OAuth
    google_app, created = SocialApp.objects.get_or_create(
        provider='google',
        defaults={
            'name': 'Google OAuth',
            'client_id': google_client_id,
            'secret': google_client_secret,
        }
    )
    
    if not created:
        # Обновляем существующий
        google_app.client_id = google_client_id
        google_app.secret = google_client_secret
        google_app.save()
        print("✅ Google OAuth app обновлен")
    else:
        print("✅ Google OAuth app создан")
    
    # Добавляем site к social app
    if site not in google_app.sites.all():
        google_app.sites.add(site)
        print(f"✅ Site добавлен к Google OAuth app")
    
    print()
    print("=" * 60)
    print("✅ Google OAuth настроен успешно!")
    print("=" * 60)
    print()
    print("📝 Важные URL для настройки в Google Cloud Console:")
    print()
    print("1️⃣  Authorized JavaScript origins:")
    print(f"   https://{domain}")
    print()
    print("2️⃣  Authorized redirect URIs:")
    print(f"   https://{domain}/accounts/google/login/callback/")
    print()
    print("=" * 60)
    print()
    print("🔍 Проверка конфигурации:")
    print(f"   Site ID: {site.id}")
    print(f"   Site Domain: {site.domain}")
    print(f"   Provider: {google_app.provider}")
    print(f"   Client ID: {google_app.client_id[:20]}...")
    print(f"   Sites: {[s.domain for s in google_app.sites.all()]}")
    print()
    print("🧪 Тестирование:")
    print(f"   1. Откройте: https://{domain}/accounts/google/login/")
    print("   2. Должен произойти редирект на Google")
    print("   3. После авторизации должен создаться пользователь")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = setup_google_oauth()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
