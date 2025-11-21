#!/usr/bin/env python3
"""
Скрипт для генерации безопасных секретов для production окружения
"""
import secrets
import string

def generate_django_secret_key(length=50):
    """Генерирует безопасный Django SECRET_KEY"""
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(length))

def generate_strong_password(length=32):
    """Генерирует сильный пароль"""
    chars = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(secrets.choice(chars) for _ in range(length))

def generate_api_key(length=40):
    """Генерирует API ключ"""
    return secrets.token_urlsafe(length)

def main():
    print("=" * 60)
    print("🔐 Генератор секретов для UnitySphere Production")
    print("=" * 60)
    print()
    
    print("📝 ВАЖНО: Сохраните эти значения в безопасном месте!")
    print("⚠️  Эти значения больше НЕ БУДУТ показаны!")
    print()
    
    # Django Secret Key
    django_secret = generate_django_secret_key()
    print("1️⃣  DJANGO_SECRET_KEY:")
    print(f"   {django_secret}")
    print()
    
    # PostgreSQL Password
    postgres_pass = generate_strong_password()
    print("2️⃣  POSTGRES_PASSWORD:")
    print(f"   {postgres_pass}")
    print()
    
    # Redis Password (для будущего использования)
    redis_pass = generate_strong_password(24)
    print("3️⃣  REDIS_PASSWORD (для будущего):")
    print(f"   {redis_pass}")
    print()
    
    # API Token для внутренних сервисов
    api_token = generate_api_key()
    print("4️⃣  INTERNAL_API_TOKEN:")
    print(f"   {api_token}")
    print()
    
    print("=" * 60)
    print("📋 Шаблон для .env файла:")
    print("=" * 60)
    print()
    print("# Django Configuration")
    print(f"DJANGO_SECRET_KEY={django_secret}")
    print("DEBUG=False")
    print()
    print("# Database Configuration")
    print("POSTGRES_NAME=unitysphere_prod")
    print("POSTGRES_USER=unitysphere_user")
    print(f"POSTGRES_PASSWORD={postgres_pass}")
    print("POSTGRES_HOST=fnclub-db")
    print("POSTGRES_PORT=5432")
    print()
    print("# Redis Configuration (optional)")
    print(f"REDIS_PASSWORD={redis_pass}")
    print("REDIS_HOST=redis")
    print("REDIS_PORT=6379")
    print()
    print("# Security")
    print(f"INTERNAL_API_TOKEN={api_token}")
    print()
    print("# Google OAuth (ЗАПОЛНИТЕ РЕАЛЬНЫМИ ЗНАЧЕНИЯМИ)")
    print("GOOGLE_CLIENT_ID=your-client-id-here")
    print("GOOGLE_CLIENT_SECRET=your-client-secret-here")
    print()
    print("# OpenAI (ИСПОЛЬЗУЙТЕ ВАШ PRODUCTION KEY)")
    print("OPENAI_API_KEY=sk-your-openai-key-here")
    print("OPENAI_MODEL=gpt-4o-mini")
    print()
    print("# Domain Configuration")
    print("ALLOWED_HOSTS=your-domain.com,www.your-domain.com")
    print("CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com")
    print()
    print("=" * 60)
    print("✅ Секреты успешно сгенерированы!")
    print("=" * 60)
    print()
    print("🔒 Следующие шаги:")
    print("1. Скопируйте секреты в файл .env.production")
    print("2. Заполните Google OAuth credentials")
    print("3. Добавьте ваш OpenAI API ключ")
    print("4. Укажите ваш домен в ALLOWED_HOSTS")
    print("5. НЕ коммитьте .env.production в Git!")
    print()

if __name__ == "__main__":
    main()
