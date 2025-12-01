#!/usr/bin/env python3
"""
🔧 УПРОЩЕННЫЙ СКРИПТ: Создание базовых данных
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
from django.contrib.auth import get_user_model

def create_basic_data():
    print("🚀 Создание базовых данных для UnitySphere...")

    # 1. Создаем категории клубов (только имя)
    print("📝 Создаем категории клубов...")
    categories_data = [
        'Музыка', 'Спорт', 'Игры', 'Кино', 'Книги',
        'Технологии', 'Искусство', 'Образование', 'Еда', 'Путешествия'
    ]

    categories = []
    for cat_name in categories_data:
        cat, created = ClubCategory.objects.get_or_create(
            name=cat_name
        )
        categories.append(cat)
        if created:
            print(f"  ✅ Создана категория: {cat_name}")
        else:
            print(f"  ℹ️ Найдена категория: {cat_name}")

    # 2. Создаем города
    print("\n🏙️ Создаем города...")
    cities_data = [
        'Алматы', 'Астана', 'Шымкент', 'Караганда', 'Актобе',
        'Тараз', 'Павлодар', 'Семей', 'Атырау', 'Усть-Каменогорск'
    ]

    cities = []
    for city_name in cities_data:
        city, created = City.objects.get_or_create(
            name=city_name
        )
        cities.append(city)
        if created:
            print(f"  ✅ Создан город: {city_name}")
        else:
            print(f"  ℹ️ Найден город: {city_name}")

    # 3. Создаем пользователей
    print("\n 👥 Создаем пользователей...")
    users_data = [
        {
            'email': 'music.lover@fan-club.kz',
            'first_name': 'Айжан',
            'last_name': 'Музыкальная',
            'phone': '+7 (701) 123-45-67',
            'password': 'testpass123'
        },
        {
            'email': 'sports.kz@fan-club.kz',
            'first_name': 'Данияр',
            'last_name': 'Спортивный',
            'phone': '+7 (701) 234-56-78',
            'password': 'testpass123'
        },
        {
            'email': 'gamer.pro@fan-club.kz',
            'first_name': 'Арман',
            'last_name': 'Игроман',
            'phone': '+7 (701) 345-67-89',
            'password': 'testpass123'
        }
    ]

    users = []
    for user_data in users_data:
        try:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'phone': user_data['phone'],
                    'is_active': True,
                    'username': user_data['email']  # Используем email как username
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                print(f"  ✅ Создан пользователь: {user_data['email']}")
            else:
                print(f"  ℹ️ Найден пользователь: {user_data['email']}")
            users.append(user)
        except Exception as e:
            print(f"  ❌ Ошибка с пользователем {user_data['email']}: {e}")

    # 4. Создаем клубы
    print("\n🏆 Создаем клубы...")
    clubs_data = [
        {
            'name': 'Клуб любителей казахской музыки',
            'description': 'Объединяем ценителей традиционной и современной казахской музыки.',
            'category': 'Музыка',
            'city': 'Алматы',
            'email': 'music.kz@fan-club.kz',
            'phone': '+7 (701) 111-22-33',
            'address': 'Алматы, проспект Абая 89',
            'activities': 'Концерты, музыкальные вечера, мастер-классы',
            'target_audience': '18-35 лет, любители казахской культуры',
            'skills_developed': 'Музыкальный вкус, культурная осведомленность',
            'tags': 'музыка, казахская культура, традиции'
        },
        {
            'name': 'Баскетбольный клуб "Алматы Stars"',
            'description': 'Городская баскетбольная команда для любителей и профессионалов.',
            'category': 'Спорт',
            'city': 'Алматы',
            'email': 'basketball@fan-club.kz',
            'phone': '+7 (701) 222-33-44',
            'address': 'Алматы, ул. Букейханова 128',
            'activities': 'Тренировки, турниры, товарищеские матчи',
            'target_audience': '16-40 лет, любители баскетбола',
            'skills_developed': 'Физическая форма, командная работа',
            'tags': 'баскетбол, спорт, здоровый образ жизни'
        },
        {
            'name': 'Киберспортивный клуб "KZ Gamers"',
            'description': 'Объединяем киберспортсменов Казахстана.',
            'category': 'Игры',
            'city': 'Астана',
            'email': 'cyber@fan-club.kz',
            'phone': '+7 (701) 333-44-55',
            'address': 'Астана, проспект dependent 56',
            'activities': 'Кибертурниры, стримы, обучающие воркшопы',
            'target_audience': '14-28 лет, киберспортсмены и геймеры',
            'skills_developed': 'Реакция, стратегическое мышление',
            'tags': 'киберспорт, игры, турниры'
        }
    ]

    created_clubs = []
    for club_data in clubs_data:
        try:
            category = ClubCategory.objects.get(name=club_data['category'])
            city = City.objects.get(name=club_data['city'])
            creator = users[0] if users else None

            club = Club.objects.create(
                name=club_data['name'],
                description=club_data['description'],
                email=club_data['email'],
                phone=club_data['phone'],
                address=club_data['address'],
                category=category,
                city=city,
                creater=creator,
                activities=club_data['activities'],
                target_audience=club_data['target_audience'],
                skills_developed=club_data['skills_developed'],
                tags=club_data['tags'],
                is_active=True,
                is_private=False,
                members_count=20 + len(created_clubs) * 10,
                likes_count=30 + len(created_clubs) * 15,
                partners_count=5 + len(created_clubs) * 3
            )
            created_clubs.append(club)
            print(f"  ✅ Создан клуб: {club_data['name']}")
        except Exception as e:
            print(f"  ❌ Ошибка с клубом {club_data['name']}: {e}")

    print(f"\n🎉 Готово! Создано:")
    print(f"  - {len(categories)} категорий клубов")
    print(f"  - {len(cities)} городов")
    print(f"  - {len(users)} пользователей")
    print(f"  - {len(created_clubs)} реальных клубов")

    return {
        'categories': len(categories),
        'cities': len(cities),
        'users': len(users),
        'clubs': len(created_clubs)
    }

if __name__ == '__main__':
    create_basic_data()