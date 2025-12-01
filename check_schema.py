#!/usr/bin/env python3
"""
🔍 ПРОВЕРКА СХЕМЫ БАЗЫ ДАННЫХ КЛУБОВ
"""

import os
import sys
from pathlib import Path

# Добавляем путь к Django проекту
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.db import connection

def check_club_schema():
    """Проверяем схему таблицы клубов"""
    print("🔍 ПРОВЕРКА СХЕМЫ ТАБЛИЦЫ КЛУБОВ")
    print("=" * 50)

    with connection.cursor() as cursor:
        # Получаем информацию о таблице clubs_club
        cursor.execute("""
            PRAGMA table_info(clubs_club)
        """)
        columns = cursor.fetchall()

        print("Структура таблицы clubs_club:")
        for col in columns:
            cid, name, type_, notnull, dflt_value, pk = col
            print(f"  {name}: {type_} | NOT NULL: {notnull} | DEFAULT: {dflt_value} | PK: {pk}")

        print("\n" + "="*50)

        # Проверяем конкретное поле activities
        cursor.execute("""
            SELECT name, type, notnull, dflt_value
            FROM pragma_table_info('clubs_club')
            WHERE name = 'activities'
        """)
        activities_info = cursor.fetchone()
        if activities_info:
            name, type_, notnull, dflt_value = activities_info
            print(f"Поле 'activities': {type_} | NOT NULL: {notnull} | DEFAULT: {dflt_value}")

if __name__ == "__main__":
    try:
        check_club_schema()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()