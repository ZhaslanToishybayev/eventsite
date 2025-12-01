#!/usr/bin/env python3
"""
🔍 ДЕБАГИНГ СОЗДАНИЯ КЛУБА
"""

import os
import sys
from pathlib import Path

# Добавляем путь к Django проекту
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from actionable_ai_consultant import ActionableAIConsultant
from clubs.models import Club

def debug_club_creation():
    """Отлаживаем создание клуба"""
    print("🔍 ДЕБАГИНГ СОЗДАНИЯ КЛУБА")
    print("=" * 40)

    ai = ActionableAIConsultant()

    # Тестовые данные для клуба
    test_club_info = {
        'name': 'Тестовый Клуб Дебаг',
        'description': 'Тестовый клуб для отладки создания',
        'category': 'Технологии',
        'city': 'Алматы',
        'email': 'debug@test.kz',
        'phone': '+77010000001',
        'address': 'Алматы, тестовый адрес',
        'activities': 'Тестовые мероприятия',
        'target_audience': 'Тестовая аудитория',
        'skills_developed': 'Тестовые навыки',
        'tags': 'тест, дебаг'
    }

    print("📋 Тестовые данные:")
    for key, value in test_club_info.items():
        print(f"  {key}: {value}")

    print("\n🚀 Попытка создания клуба...")
    result = ai.create_club_in_database(test_club_info, "debug@test.kz")

    print(f"\n📊 Результат: {result}")

    # Проверяем, создался ли клуб в базе
    if result['success']:
        try:
            club = Club.objects.get(id=result['club_id'])
            print(f"\n✅ Клуб найден в базе:")
            print(f"  ID: {club.id}")
            print(f"  Name: {club.name}")
            print(f"  Activities: '{club.activities}'")
            print(f"  Email: {club.email}")
        except Club.DoesNotExist:
            print("\n❌ Клуб не найден в базе данных")
    else:
        print(f"\n❌ Ошибка: {result['error']}")

if __name__ == "__main__":
    try:
        debug_club_creation()
    except Exception as e:
        print(f"\n❌ Фатальная ошибка: {e}")
        import traceback
        traceback.print_exc()