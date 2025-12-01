#!/usr/bin/env python3
"""
🎯 Database Comparison Tool - Сравнение PostgreSQL дампа с текущей SQLite базой

Этот скрипт анализирует и сравнивает две базы данных:
1. PostgreSQL дамп (postgres_backup_2025-11-21.sql)
2. Текущая SQLite база (db.sqlite3)

Позволяет выявить различия в структуре и данных для принятия решений о миграции.
"""

import os
import sys
import django
import re
import json
from collections import defaultdict

# Добавляем путь к Django проекту
sys.path.append('/var/www/myapp/eventsite')

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
# from django.core.management.color import no_style
# from django.core.management.sql import sql_indexes
# from django.db import models

def analyze_postgres_dump():
    """Анализирует PostgreSQL дамп"""
    print("🗄️ АНАЛИЗ POSTGRESQL ДАМПА")
    print("=" * 60)

    try:
        with open('/var/www/myapp/eventsite/postgres_backup_2025-11-21.sql', 'r', encoding='utf-8') as f:
            content = f.read()

        # Извлекаем таблицы
        tables = re.findall(r'CREATE TABLE public\.(\w+)', content)
        print(f"📋 Найдено таблиц в PostgreSQL: {len(tables)}")
        print("Таблицы PostgreSQL:")
        for i, table in enumerate(sorted(tables), 1):
            print(f"  {i:2d}. {table}")

        # Анализируем структуру важных таблиц
        table_structures = {}

        for table_name in ['clubs_club', 'clubs_city', 'clubs_clubcategory',
                          'clubs_festival', 'clubs_publication', 'accounts_user']:
            pattern = rf'CREATE TABLE public\.{table_name} \((.*?)\);'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                fields_text = match.group(1)
                fields = re.findall(r'(\w+)\s+([A-Z_()]+(?:\s*\w+)?)', fields_text)
                table_structures[table_name] = {
                    'fields': [(field[0], field[1]) for field in fields],
                    'has_data': '-- Data:' in content or f'COPY {table_name}' in content
                }

        print(f"\n🏗️ СТРУКТУРА ВАЖНЫХ ТАБЛИЦ POSTGRESQL:")
        print("-" * 50)

        for table_name, info in table_structures.items():
            print(f"\n📋 {table_name}:")
            print(f"   Поля: {len(info['fields'])}")
            for field_name, field_type in info['fields'][:10]:  # Первые 10 полей
                print(f"     • {field_name} ({field_type})")
            if len(info['fields']) > 10:
                print(f"     ... и еще {len(info['fields']) - 10} полей")
            print(f"   Содержит данные: {'Да' if info.get('has_data', False) else 'Нет'}")

        return {
            'tables': tables,
            'structures': table_structures,
            'total_tables': len(tables)
        }

    except Exception as e:
        print(f"❌ Ошибка анализа PostgreSQL дампа: {e}")
        return None

def analyze_sqlite_database():
    """Анализирует текущую SQLite базу"""
    print(f"\n🗄️ АНАЛИЗ ТЕКУЩЕЙ SQLite БАЗЫ")
    print("=" * 60)

    try:
        # Получаем список таблиц
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            sqlite_tables = [row[0] for row in cursor.fetchall()]

        print(f"📋 Найдено таблиц в SQLite: {len(sqlite_tables)}")
        print("Таблицы SQLite:")
        for i, table in enumerate(sorted(sqlite_tables), 1):
            print(f"  {i:2d}. {table}")

        # Анализируем Django модели
        django_models = []
        for app_config in django.apps.apps.get_app_configs():
            for model in app_config.get_models():
                django_models.append(f"{app_config.label}.{model._meta.model_name}")

        print(f"\n🏗️ СТРУКТУРА DJANGO МОДЕЛЕЙ:")
        print("-" * 50)

        model_structures = {}
        for app_config in django.apps.apps.get_app_configs():
            for model in app_config.get_models():
                if model._meta.label in ['clubs', 'accounts', 'publications', 'festivals']:
                    fields = [(field.name, type(field).__name__) for field in model._meta.get_fields()]
                    model_name = f"{app_config.label}.{model._meta.model_name}"
                    model_structures[model_name] = {
                        'fields': fields,
                        'table_name': model._meta.db_table,
                        'count': model.objects.count() if hasattr(model.objects, 'count') else 0
                    }

        for model_name, info in model_structures.items():
            print(f"\n📋 {model_name} (таблица: {info['table_name']}):")
            print(f"   Поля: {len(info['fields'])}")
            print(f"   Записей: {info['count']}")
            for field_name, field_type in info['fields'][:8]:  # Первые 8 полей
                print(f"     • {field_name} ({field_type})")
            if len(info['fields']) > 8:
                print(f"     ... и еще {len(info['fields']) - 8} полей")

        return {
            'tables': sqlite_tables,
            'models': model_structures,
            'total_tables': len(sqlite_tables)
        }

    except Exception as e:
        print(f"❌ Ошибка анализа SQLite базы: {e}")
        return None

def compare_databases(pg_data, sqlite_data):
    """Сравнивает две базы данных"""
    print(f"\n🔍 СРАВНЕНИЕ БАЗ ДАННЫХ")
    print("=" * 60)

    if not pg_data or not sqlite_data:
        print("❌ Не удалось проанализировать одну из баз данных")
        return

    # Сравнение таблиц
    pg_tables = set(pg_data['tables'])
    sqlite_tables = set(sqlite_data['tables'])

    only_in_pg = pg_tables - sqlite_tables
    only_in_sqlite = sqlite_tables - pg_tables
    common_tables = pg_tables & sqlite_tables

    print(f"\n📊 СТАТИСТИКА ТАБЛИЦ:")
    print(f"   Только в PostgreSQL: {len(only_in_pg)}")
    print(f"   Только в SQLite: {len(only_in_sqlite)}")
    print(f"   Общие таблицы: {len(common_tables)}")

    if only_in_pg:
        print(f"\n🔴 Таблицы ТОЛЬКО в PostgreSQL:")
        for table in sorted(only_in_pg):
            print(f"   • {table}")

    if only_in_sqlite:
        print(f"\n🔵 Таблицы ТОЛЬКО в SQLite:")
        for table in sorted(only_in_sqlite):
            print(f"   • {table}")

    # Сравнение структуры моделей
    print(f"\n🏗️ СРАВНЕНИЕ СТРУКТУР МОДЕЛЕЙ:")
    print("-" * 50)

    # Ключевые модели для сравнения
    key_models = {
        'clubs_club': 'clubs.club',
        'clubs_city': 'clubs.city',
        'clubs_clubcategory': 'clubs.clubcategory',
        'accounts_user': 'accounts.user'
    }

    for pg_table, django_model in key_models.items():
        if pg_table in pg_data['structures'] and django_model in sqlite_data['models']:
            pg_fields = set(field[0] for field in pg_data['structures'][pg_table]['fields'])
            django_fields = set(field[0] for field in sqlite_data['models'][django_model]['fields'])

            only_in_pg = pg_fields - django_fields
            only_in_django = django_fields - pg_fields
            common_fields = pg_fields & django_fields

            print(f"\n📋 {pg_table} vs {django_model}:")
            print(f"   Общие поля: {len(common_fields)}")
            print(f"   Только в PostgreSQL: {len(only_in_pg)} {list(only_in_pg) if only_in_pg else '(-)'}")
            print(f"   Только в Django: {len(only_in_django)} {list(only_in_django) if only_in_django else '(-)'}")

    # Анализ данных
    print(f"\n📊 АНАЛИЗ ДАННЫХ:")
    print("-" * 50)

    for model_name, info in sqlite_data['models'].items():
        if info['count'] > 0:
            print(f"   • {model_name}: {info['count']} записей")

def generate_migration_recommendations(pg_data, sqlite_data):
    """Генерирует рекомендации по миграции"""
    print(f"\n💡 РЕКОМЕНДАЦИИ ПО МИГРАЦИИ")
    print("=" * 60)

    if not pg_data or not sqlite_data:
        print("❌ Не удалось проанализировать базы данных для генерации рекомендаций")
        return

    recommendations = []

    # Проверка на наличие более полной структуры в PostgreSQL
    pg_tables = set(pg_data['tables'])
    sqlite_tables = set(sqlite_data['tables'])

    if len(pg_tables) > len(sqlite_tables):
        recommendations.append("✅ PostgreSQL содержит больше таблиц - рекомендуется миграция")

    # Проверка на наличие расширенных моделей
    key_models = ['clubs_club', 'clubs_city', 'clubs_clubcategory']
    extended_models = []

    for model in key_models:
        if model in pg_data['structures']:
            pg_field_count = len(pg_data['structures'][model]['fields'])
            # Поиск соответствующей Django модели
            for django_model, info in sqlite_data['models'].items():
                if model in django_model or model.replace('_', '') in django_model.replace('.', ''):
                    django_field_count = len(info['fields'])
                    if pg_field_count > django_field_count:
                        extended_models.append((model, pg_field_count, django_field_count))

    if extended_models:
        recommendations.append(f"✅ PostgreSQL модели содержат больше полей:")
        for model, pg_count, django_count in extended_models:
            recommendations.append(f"   • {model}: {pg_count} vs {django_count} полей")

    # Проверка на наличие данных
    has_data_in_sqlite = any(info['count'] > 0 for info in sqlite_data['models'].values())
    has_data_in_pg = any(info.get('has_data', False) for info in pg_data['structures'].values())

    if has_data_in_pg and not has_data_in_sqlite:
        recommendations.append("✅ PostgreSQL содержит данные, а SQLite - нет")
    elif has_data_in_sqlite and has_data_in_pg:
        recommendations.append("✅ Обе базы содержат данные - требуется careful миграция")

    print("📋 Рекомендации:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")

    # Генерация плана действий
    print(f"\n📋 ПЛАН ДЕЙСТВИЙ:")
    print("-" * 30)
    print("1. 📊 Создать резервную копию текущей SQLite базы")
    print("2. 🔍 Проверить целостность данных в PostgreSQL дампе")
    print("3. 🛠️  Создать Django миграции для расширенной структуры")
    print("4. 📤 Перенести данные из PostgreSQL в SQLite")
    print("5. ✅ Проверить работоспособность всех функций")
    print("6. 🚀 Развернуть обновленную систему")

def main():
    """Основная функция"""
    print("🎯 Database Comparison Tool v1.0")
    print("Сравнение PostgreSQL дампа с текущей SQLite базой")
    print("=" * 80)

    # Анализ PostgreSQL дампа
    pg_data = analyze_postgres_dump()

    # Анализ SQLite базы
    sqlite_data = analyze_sqlite_database()

    # Сравнение баз данных
    compare_databases(pg_data, sqlite_data)

    # Генерация рекомендаций
    generate_migration_recommendations(pg_data, sqlite_data)

    print(f"\n✅ АНАЛИЗ ЗАВЕРШЕН")
    print("💾 Сохранен подробный отчет в database_comparison_report.json")

    # Сохранение отчета
    report = {
        'postgres_analysis': pg_data,
        'sqlite_analysis': sqlite_data,
        'comparison_summary': {
            'postgres_tables_count': len(pg_data['tables']) if pg_data else 0,
            'sqlite_tables_count': len(sqlite_data['tables']) if sqlite_data else 0,
        }
    }

    with open('/var/www/myapp/eventsite/database_comparison_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()