#!/usr/bin/env python3
"""
🔍 ДЕТАЛЬНАЯ ПРОВЕРКА ПОЛЬЗОВАТЕЛЕЙ
"""

import os
import sys
from pathlib import Path

# Добавляем путь к Django проекту
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def check_user_details():
    """Проверяем детали пользователей"""
    print("🔍 ДЕТАЛЬНАЯ ПРОВЕРКА ПОЛЬЗОВАТЕЛЕЙ")
    print("=" * 50)

    users = User.objects.all()
    for user in users:
        print(f"\n👤 Пользователь ID: {user.id}")
        print(f"   Имя: {user.first_name}")
        print(f"   Фамилия: {user.last_name}")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Администратор: {user.is_staff}")
        print(f"   Суперпользователь: {user.is_superuser}")

if __name__ == "__main__":
    try:
        check_user_details()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()