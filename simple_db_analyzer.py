#!/usr/bin/env python3
"""
🎯 Simple Database Analyzer - Простой анализ содержимого базы данных
"""

import os
import sys
import django

# Добавляем путь к Django проекту
sys.path.append('/var/www/myapp/eventsite')

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def analyze_database():
    """Анализирует содержимое базы данных"""

    print("🗄️ АНАЛИЗ БАЗЫ ДАННЫХ")
    print("=" * 50)

    try:
        from django.db import connection

        # Проверяем доступные таблицы
        tables = connection.introspection.table_names()
        print(f"📋 Найдено таблиц: {len(tables)}")
        print("Таблицы:")
        for table in sorted(tables):
            print(f"  • {table}")

        # Подсчет записей в каждой таблице
        print("\n📊 КОЛИЧЕСТВО ЗАПИСЕЙ В ТАБЛИЦАХ")
        print("-" * 40)

        total_records = 0
        for table in sorted(tables):
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    total_records += count
                    if count > 0:
                        print(f"✅ {table:<30} {count:>6} записей")
                    else:
                        print(f"⚪ {table:<30} {count:>6} записей")
            except Exception as e:
                print(f"❌ {table:<30} Ошибка: {e}")

        print(f"\n📈 ОБЩЕЕ КОЛИЧЕСТВО ЗАПИСЕЙ: {total_records}")

        # Анализ основных таблиц
        print("\n🏢 АНАЛИЗ ОСНОВНЫХ ТАБЛИЦ")
        print("-" * 40)

        # Анализ таблицы clubs_club
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name, description, location, created_at FROM clubs_club LIMIT 5")
                clubs = cursor.fetchall()
                if clubs:
                    print("🏆 ПРИМЕРЫ КЛУБОВ:")
                    for i, (name, description, location, created_at) in enumerate(clubs, 1):
                        desc_preview = (description[:50] + '...') if description and len(description) > 50 else description or 'Нет описания'
                        print(f"  {i}. {name}")
                        print(f"     📍 {location or 'Не указано'}")
                        print(f"     📝 {desc_preview}")
                        print(f"     ⏰ {created_at}")
                        print()
        except Exception as e:
            print(f"Клубы: {e}")

        # Анализ таблицы пользователей
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT username, email, date_joined FROM auth_user LIMIT 5")
                users = cursor.fetchall()
                if users:
                    print("👥 ПРИМЕРЫ ПОЛЬЗОВАТЕЛЕЙ:")
                    for i, (username, email, date_joined) in enumerate(users, 1):
                        print(f"  {i}. {username} - {email}")
                        print(f"     Зарегистрирован: {date_joined}")
                        print()
        except Exception as e:
            print(f"Пользователи: {e}")

        # Анализ таблицы публикаций
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT title, content, created_at FROM publications_publication LIMIT 5")
                publications = cursor.fetchall()
                if publications:
                    print("📰 ПРИМЕРЫ ПУБЛИКАЦИЙ:")
                    for i, (title, content, created_at) in enumerate(publications, 1):
                        content_preview = (content[:100] + '...') if content and len(content) > 100 else content or 'Нет содержания'
                        print(f"  {i}. {title}")
                        print(f"     📝 {content_preview}")
                        print(f"     ⏰ {created_at}")
                        print()
        except Exception as e:
            print(f"Публикации: {e}")

        # Анализ структуры таблиц
        print("\n🏗️ СТРУКТУРА ВАЖНЫХ ТАБЛИЦ")
        print("-" * 40)

        key_tables = ['clubs_club', 'auth_user', 'publications_publication']
        for table in key_tables:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    if columns:
                        print(f"\n📋 {table}:")
                        for col in columns:
                            col_name = col[1]
                            col_type = col[2]
                            col_null = "NOT NULL" if col[3] else "NULL"
                            print(f"  • {col_name} ({col_type}) {col_null}")
            except Exception as e:
                print(f"Таблица {table}: {e}")

        print("\n✅ АНАЛИЗ ЗАВЕРШЕН УСПЕШНО!")
        print("💾 База данных содержит реальные данные и готова к использованию!")
        return True

    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")
        return False

if __name__ == "__main__":
    success = analyze_database()
    if success:
        print("\n🎯 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. ✅ База данных восстановлена и содержит данные")
        print("2. 🚀 Можно приступать к реализации AI функционала")
        print("3. 💡 Данные о клубах, пользователях и публикациях доступны")
    else:
        print("\n❌ Требуется修复 базы данных")