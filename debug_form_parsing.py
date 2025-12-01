#!/usr/bin/env python3
"""
🔍 ДЕБАГИНГ ПАРСИНГА ФОРМЫ
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

def debug_form_parsing():
    """Отлаживаем парсинг формы"""
    print("🔍 ДЕБАГИНГ ПАРСИНГА ФОРМЫ")
    print("=" * 40)

    ai = ActionableAIConsultant()

    # Форма из теста
    club_form = """Название клуба: Кодеры Будущего
Описание клуба: Клуб для молодых программистов и энтузиастов технологий. Мы проводим хакатоны, обучающие сессии, code review и помогаем в трудоустройстве в IT-сфере. Присоединяйся к сообществу единомышленников!

Категория: Технологии
Город: Алматы
Email клуба: coders.future.almaty@gmail.com
Телефон: +7 (701) 123-45-67
Адрес: Алматы, проспект Достык 123
Деятельность: Обучение программированию, хакатоны, менторство
Целевая аудитория: Молодые программисты 18-35 лет
Развиваемые навыки: Программирование, teamwork, problem-solving
Теги: programming, python, javascript, hackathons"""

    print("📋 Исходная форма:")
    print(club_form)

    print("\n🔍 Результат парсинга:")
    club_info = ai.extract_club_info(club_form)

    for key, value in club_info.items():
        print(f"  {key}: '{value}'")

    # Проверяем, есть ли activities
    if 'activities' not in club_info or club_info.get('activities') is None:
        print("\n❌ Поле 'activities' не найдено!")
    else:
        print(f"\n✅ Поле 'activities' найдено: '{club_info['activities']}'")

    # Проверяем соответствие ключей
    expected_keys = ['name', 'description', 'category', 'city', 'email', 'phone', 'address', 'activities', 'target_audience', 'skills_developed', 'tags']
    print("\n🔍 Проверка ключей:")
    for key in expected_keys:
        if key in club_info:
            print(f"  ✅ {key}: '{club_info[key]}'")
        else:
            print(f"  ❌ {key}: отсутствует")

if __name__ == "__main__":
    try:
        debug_form_parsing()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()