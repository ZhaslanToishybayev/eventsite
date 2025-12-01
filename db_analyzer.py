#!/usr/bin/env python3
"""
🎯 Database Analyzer - Анализ содержимого базы данных
"""

import os
import sys
import django
from django.conf import settings

# Добавляем путь к Django проекту
sys.path.append('/var/www/myapp/eventsite')

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from clubs.models import Club
from festivals.models import Festival
from publications.models import Publication

def analyze_database():
    """Анализирует содержимое базы данных"""

    print("🗄️ АНАЛИЗ БАЗЫ ДАННЫХ")
    print("=" * 50)

    try:
        # Проверяем доступные таблицы
        tables = connection.introspection.table_names()
        print(f"📋 Найдено таблиц: {len(tables)}")
        print("Таблицы:")
        for table in sorted(tables):
            print(f"  • {table}")

        print("\n🏢 АНАЛИЗ КЛУБОВ")
        print("-" * 30)

        # Анализ клубов
        clubs_count = Club.objects.count()
        print(f"Количество клубов: {clubs_count}")

        if clubs_count > 0:
            clubs = Club.objects.all()[:5]  # Первые 5 клубов
            print("\nПримеры клубов:")
            for club in clubs:
                print(f"  • {club.name} - {club.description[:50]}...")
                print(f"    Категория: {getattr(club, 'category', 'N/A')}")
                print(f"    Местоположение: {getattr(club, 'location', 'N/A')}")
                print(f"    Создан: {club.created_at}")
                print()

        print("\n🎉 АНАЛИЗ МЕРОПРИЯТИЙ")
        print("-" * 30)

        # Анализ мероприятий (если модель существует)
        try:
            festivals_count = Festival.objects.count()
            print(f"Количество мероприятий: {festivals_count}")

            if festivals_count > 0:
                festivals = Festival.objects.all()[:5]  # Первые 5 мероприятий
                print("\nПримеры мероприятий:")
                for festival in festivals:
                    print(f"  • {festival.title} - {festival.description[:50]}...")
                    print(f"    Дата: {getattr(festival, 'date', 'N/A')}")
                    print(f"    Местоположение: {getattr(festival, 'location', 'N/A')}")
                    print()
        except Exception as e:
            print(f"Мероприятия: {e}")

        print("\n📰 АНАЛИЗ ПУБЛИКАЦИЙ")
        print("-" * 30)

        # Анализ публикаций (если модель существует)
        try:
            publications_count = Publication.objects.count()
            print(f"Количество публикаций: {publications_count}")

            if publications_count > 0:
                publications = Publication.objects.all()[:5]  # Первые 5 публикаций
                print("\nПримеры публикаций:")
                for publication in publications:
                    print(f"  • {publication.title}")
                    print(f"    Тип: {getattr(publication, 'content_type', 'N/A')}")
                    print(f"    Создан: {publication.created_at}")
                    print()
        except Exception as e:
            print(f"Публикации: {e}")

        print("\n📊 СТАТИСТИКА")
        print("-" * 30)

        # Общая статистика
        total_records = 0
        for table in tables:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                total_records += count
                if count > 0:
                    print(f"{table}: {count} записей")

        print(f"\nОбщее количество записей: {total_records}")

        # Проверяем структуру моделей
        print("\n🏗️ СТРУКТУРА МОДЕЛЕЙ")
        print("-" * 30)

        try:
            club_fields = [field.name for field in Club._meta.fields]
            print(f"Club model fields: {', '.join(club_fields)}")
        except Exception as e:
            print(f"Club model error: {e}")

        try:
            festival_fields = [field.name for field in Festival._meta.fields]
            print(f"Festival model fields: {', '.join(festival_fields)}")
        except Exception as e:
            print(f"Festival model error: {e}")

        print("\n✅ АНАЛИЗ ЗАВЕРШЕН")
        return True

    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")
        return False

if __name__ == "__main__":
    analyze_database()