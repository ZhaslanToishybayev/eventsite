#!/usr/bin/env python3
"""
🎯 Test Database API - Проверка доступности данных из базы через Django ORM
"""

import os
import sys
import django

# Добавляем путь к Django проекту
sys.path.append('/var/www/myapp/eventsite')

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from clubs.models import Club, ClubCategory, City
from django.http import JsonResponse
from django.core.serializers import serialize
import json

def test_clubs_data():
    """Тестирование доступности данных о клубах"""
    print("🧪 ТЕСТИРОВАНИЕ ДАННЫХ О КЛУБАХ")
    print("=" * 50)

    try:
        # Получаем все клубы
        clubs = Club.objects.all()
        print(f"📋 Найдено клубов: {clubs.count()}")

        if clubs.exists():
            print("\n🏆 ПРИМЕРЫ КЛУБОВ:")
            for i, club in enumerate(clubs[:3], 1):
                print(f"  {i}. {club.name}")
                print(f"     📍 {club.city.name if club.city else 'Не указан'}")
                print(f"     🏷️ {club.category.name if club.category else 'Не указана'}")
                print(f"     👥 {club.members_count} участников")
                print(f"     📝 {club.description[:100]}...")
                print()

            # Проверяем категории
            categories = ClubCategory.objects.all()
            print(f"🏷️ Найдено категорий: {categories.count()}")
            if categories.exists():
                print("Категории:")
                for cat in categories[:5]:
                    print(f"  • {cat.name}")
                print()

            # Проверяем города
            cities = City.objects.all()
            print(f"🏙️ Найдено городов: {cities.count()}")
            if cities.exists():
                print("Города:")
                for city in cities[:5]:
                    print(f"  • {city.name}")
                print()

            return True
        else:
            print("❌ Клубы не найдены в базе данных")
            return False

    except Exception as e:
        print(f"❌ Ошибка при получении данных: {e}")
        return False

def create_test_api_response():
    """Создаем тестовый API ответ для фронтенда"""
    try:
        clubs = Club.objects.filter(is_active=True)[:5]
        categories = ClubCategory.objects.all()
        cities = City.objects.all()

        # Подготавливаем данные для JSON
        clubs_data = []
        for club in clubs:
            clubs_data.append({
                'id': str(club.id),  # Конвертируем UUID в строку
                'name': club.name,
                'description': club.description[:200] + '...' if len(club.description) > 200 else club.description,
                'city': club.city.name if club.city else 'Не указан',
                'category': club.category.name if club.category else 'Не указана',
                'members_count': club.members_count,
                'is_active': club.is_active,
                'created_at': club.created_at.strftime('%Y-%m-%d')
            })

        categories_data = [{'id': str(cat.id), 'name': cat.name} for cat in categories]
        cities_data = [{'id': str(city.id), 'name': city.name} for city in cities]

        api_response = {
            'status': 'success',
            'data': {
                'clubs': clubs_data,
                'categories': categories_data,
                'cities': cities_data
            },
            'meta': {
                'total_clubs': Club.objects.filter(is_active=True).count(),
                'total_categories': categories.count(),
                'total_cities': cities.count()
            }
        }

        # Сохраняем тестовый API ответ
        with open('/var/www/myapp/eventsite/test_api_response.json', 'w', encoding='utf-8') as f:
            json.dump(api_response, f, ensure_ascii=False, indent=2)

        print("✅ Тестовый API ответ сохранен в test_api_response.json")
        return api_response

    except Exception as e:
        print(f"❌ Ошибка при создании API ответа: {e}")
        return None

def test_database_integrity():
    """Проверка целостности базы данных"""
    print("\n🔍 ПРОВЕРКА ЦЕЛОСТНОСТИ БАЗЫ ДАННЫХ")
    print("-" * 50)

    try:
        # Проверяем основные модели
        from clubs.models import Club, ClubCategory, City
        from accounts.models import User

        checks = [
            ('Клубы', Club.objects.filter(is_active=True).count()),
            ('Категории', ClubCategory.objects.count()),
            ('Города', City.objects.count()),
            ('Пользователи', User.objects.count()),
        ]

        all_good = True
        for name, count in checks:
            status = "✅" if count > 0 else "⚠️"
            print(f"{status} {name}: {count}")

            if count == 0:
                all_good = False

        print(f"\n📊 Статус базы данных: {'✅ РАБОТАЕТ' if all_good else '⚠️ ТРЕБУЕТ ВНИМАНИЯ'}")
        return all_good

    except Exception as e:
        print(f"❌ Ошибка проверки целостности: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Database API Test v1.0")
    print("Проверка доступности данных из базы данных")
    print("=" * 60)

    # Тестируем данные
    clubs_test = test_clubs_data()
    integrity_test = test_database_integrity()

    if clubs_test and integrity_test:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("💾 База данных готова для интеграции с AI системой")

        # Создаем тестовый API ответ
        api_data = create_test_api_response()
        if api_data:
            print("🌐 API данные подготовлены для фронтенда")

    else:
        print("\n❌ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("🔧 Требуется диагностика базы данных")