#!/usr/bin/env python3
"""
🔍 ПРОВЕРКА БАЗЫ ДАННЫХ ДЛЯ ТЕСТИРОВАНИЯ AI СИСТЕМЫ
"""

import os
import sys
from pathlib import Path

# Добавляем путь к Django проекту
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from clubs.models import Club, ClubCategory, City

User = get_user_model()

def check_database_status():
    """Проверяем состояние базы данных"""
    print("🔍 ПРОВЕРКА СОСТОЯНИЯ БАЗЫ ДАННЫХ")
    print("=" * 50)

    # Проверяем пользователей
    users = User.objects.all()
    print(f"\n👥 Пользователи: {users.count()}")
    if users.exists():
        for user in users[:5]:  # Показываем первых 5
            print(f"   - {user.username} ({user.email}) - {'Админ' if user.is_staff else 'Пользователь'}")

    # Проверяем категории
    categories = ClubCategory.objects.all()
    print(f"\n🏷️ Категории: {categories.count()}")
    if categories.exists():
        for category in categories[:5]:
            print(f"   - {category.name} {'(Активна)' if category.is_active else '(Неактивна)'}")

    # Проверяем города
    cities = City.objects.all()
    print(f"\n🏙️ Города: {cities.count()}")
    if cities.exists():
        for city in cities[:5]:
            print(f"   - {city.name}")

    # Проверяем клубы
    clubs = Club.objects.all()
    print(f"\n🏠 Клубы: {clubs.count()}")
    if clubs.exists():
        for club in clubs[:3]:
            print(f"   - {club.name} в {club.city.name if club.city else 'Городе'}")

    return {
        'users': users,
        'categories': categories,
        'cities': cities,
        'clubs': clubs
    }

def create_test_user():
    """Создаем тестового пользователя если нет подходящих"""
    print("\n🔧 СОЗДАНИЕ ТЕСТОВОГО ПОЛЬЗОВАТЕЛЯ")
    print("-" * 30)

    # Проверяем есть ли администраторы
    admin_users = User.objects.filter(is_staff=True)
    if admin_users.exists():
        print(f"✅ Найден администратор: {admin_users.first().username}")
        return admin_users.first()

    # Создаем тестового пользователя
    try:
        test_user = User.objects.create_user(
            username='ai_test_user',
            email='ai.test@fan-club.kz',
            password='test_password_123',
            is_staff=True,
            is_superuser=True
        )
        print(f"✅ Создан тестовый пользователь: {test_user.username}")
        return test_user
    except Exception as e:
        print(f"❌ Ошибка создания пользователя: {e}")
        return None

if __name__ == "__main__":
    try:
        # Проверяем базу данных
        db_status = check_database_status()

        # Создаем тестового пользователя если нужно
        if db_status['users'].count() == 0:
            create_test_user()
        elif not User.objects.filter(is_staff=True).exists():
            create_test_user()

        print("\n✅ ПРОВЕРКА ЗАВЕРШЕНА")
    except Exception as e:
        print(f"\n❌ Ошибка при проверке: {e}")
        import traceback
        traceback.print_exc()