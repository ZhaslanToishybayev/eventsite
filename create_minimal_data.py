#!/usr/bin/env python3
"""
🔧 СУПЕР УПРОЩЕННЫЙ СКРИПТ: Создание минимальных данных
"""

import os
import sys
import django
from pathlib import Path

# Добавляем путь к Django проекту
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Инициализируем Django
django.setup()

from clubs.models import Club, ClubCategory, City
from accounts.models import User

def create_minimal_data():
    print("🚀 Создание минимальных данных для UnitySphere...")

    # 1. Создаем несколько категорий
    print("📝 Создаем категории...")
    categories_data = ['Музыка', 'Спорт', 'Игры', 'Кино', 'Книги']

    for cat_name in categories_data:
        cat, created = ClubCategory.objects.get_or_create(name=cat_name)
        if created:
            print(f"  ✅ Создана категория: {cat_name}")
        else:
            print(f"  ℹ️ Найдена категория: {cat_name}")

    # 2. Создаем несколько городов
    print("\n🏙️ Создаем города...")
    cities_data = ['Алматы', 'Астана', 'Шымкент', 'Караганда']

    for city_name in cities_data:
        city, created = City.objects.get_or_create(name=city_name)
        if created:
            print(f"  ✅ Создан город: {city_name}")
        else:
            print(f"  ℹ️ Найден город: {city_name}")

    # 3. Создаем тестовый клуб
    print("\n🏆 Создаем тестовый клуб...")
    try:
        # Используем существующего пользователя из базы
        admin_user = User.objects.filter(email='admin@fan-club.kz').first()
        if not admin_user:
            admin_user = User.objects.filter(is_staff=True).first()

        if admin_user:
            category = ClubCategory.objects.get(name='Музыка')
            city = City.objects.get(name='Алматы')

            club, created = Club.objects.get_or_create(
                name='Тестовый музыкальный клуб',
                defaults={
                    'description': 'Тестовый клуб для демонстрации работы платформы.',
                    'email': 'test.music@fan-club.kz',
                    'phone': '+7 (701) 999-88-77',
                    'address': 'Алматы, центр города',
                    'category': category,
                    'city': city,
                    'creater': admin_user,
                    'activities': 'Тестовые мероприятия',
                    'target_audience': 'Тестовая аудитория',
                    'skills_developed': 'Тестовые навыки',
                    'tags': 'тест, музыка',
                    'is_active': True,
                    'is_private': False,
                    'members_count': 5,
                    'likes_count': 10,
                    'partners_count': 2
                }
            )

            if created:
                print(f"  ✅ Создан тестовый клуб: {club.name}")
            else:
                print(f"  ℹ️ Найден тестовый клуб: {club.name}")
        else:
            print("  ❌ Не найден администратор для создания клуба")

    except Exception as e:
        print(f"  ❌ Ошибка создания клуба: {e}")

    # Подсчет данных
    cat_count = ClubCategory.objects.count()
    city_count = City.objects.count()
    club_count = Club.objects.count()
    user_count = User.objects.count()

    print(f"\n🎉 Готово! Статистика:")
    print(f"  - Категорий: {cat_count}")
    print(f"  - Городов: {city_count}")
    print(f"  - Клубов: {club_count}")
    print(f"  - Пользователей: {user_count}")

    return True

if __name__ == '__main__':
    create_minimal_data()