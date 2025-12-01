#!/usr/bin/env python3
"""
🔍 ДЕБАГГИНГ БЕЗОПАСНОСТИ AI КОНСУЛЬТАНТА
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

def debug_security():
    """Дебаггинг безопасности AI"""
    print("🔍 ДЕБАГГИНГ БЕЗОПАСНОСТИ AI КОНСУЛЬТАНТА")
    print("=" * 60)

    ai = ActionableAIConsultant()

    # Проверяем опасные вводы
    dangerous_inputs = [
        ("", "Пустое сообщение"),
        ("   ", "Только пробелы"),
        ("<script>alert('test')</script>", "XSS атака"),
        ("DROP TABLE users;", "SQL инъекция"),
        ("javascript:alert('test')", "JavaScript инъекция"),
        ("DELETE FROM clubs WHERE 1=1", "Опасная SQL команда"),
        ("' OR '1'='1", "SQL инъекция"),
    ]

    print("\n🛡️ ПРОВЕРКА ОПАСНЫХ ВВОДОВ:")
    for test_input, description in dangerous_inputs:
        print(f"\n🔍 {description}:")
        print(f"   Ввод: {repr(test_input)}")
        response = ai.process_user_message(test_input)
        print(f"   Ответ: {response[:100]}...")

        # Проверяем, должен ли быть заблокирован
        should_be_blocked = len(test_input.strip()) == 0 or any(pattern in test_input.lower()
                    for pattern in ['<script>', 'javascript:', 'drop table', 'delete from', 'or 1=1'])

        if should_be_blocked and "недопустимое содержание" not in response.lower():
            print(f"   ❌ Должен быть заблокирован, но не был!")
        elif not should_be_blocked and len(response) > 10:
            print(f"   ✅ Разрешенный ввод, ответ получен")
        else:
            print(f"   ⚠️ Непредсказуемое поведение")

def debug_form_parsing():
    """Дебаггинг парсинга форм"""
    print("\n🔍 ДЕБАГГИНГ ПАРСИНГА ФОРМ")
    print("=" * 60)

    ai = ActionableAIConsultant()

    # Проблемные формы из тестов
    test_forms = [
        {
            'name': 'Короткая форма',
            'form': """Название: Короткий Клуб
Описание: Короткое описание
Категория: Музыка
Город: Шымкент
Email: short@club.kz""",
        },
        {
            'name': 'Форма с emoji',
            'form': """Название: 🎵 Музыкальный Клуб 🎶
Описание: Клуб для любителей музыки 🎸
Категория: 🎼 Искусство 🎨
Город: 🏙️ Алматы 🌆
Email: music@club.kz""",
        }
    ]

    print("\n📝 ПРОВЕРКА ПАРСИНГА ФОРМ:")
    for test_case in test_forms:
        print(f"\n🔍 {test_case['name']}:")
        print(f"   Форма:\n{test_case['form']}")

        club_info = ai.extract_club_info(test_case['form'])
        print(f"   Результат парсинга:")
        for key, value in club_info.items():
            if value and value != 'None':
                print(f"     {key}: '{value}'")
            else:
                print(f"     {key}: ❌ пусто")

        # Проверяем шаблоны
        print(f"   🔍 Анализ шаблонов:")
        import re
        patterns = {
            'name': r'Название[:：]\s*"?([^"\n]+)"?',
            'description': r'Описание[:：]\s*(.+?)(?=\n(?:Категория|Город|Email|$))',
            'category': r'Категория[:：]\s*([^"\n]+)',
            'city': r'Город[:：]\s*([^"\n]+)',
            'email': r'Email[:：]\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        }

        for field, pattern in patterns.items():
            match = re.search(pattern, test_case['form'], re.IGNORECASE | re.MULTILINE)
            if match:
                print(f"     ✅ {field}: '{match.group(1).strip()}'")
            else:
                print(f"     ❌ {field}: не найдено по шаблону")

if __name__ == "__main__":
    try:
        debug_security()
        debug_form_parsing()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()