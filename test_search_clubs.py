#!/usr/bin/env python
"""
Тест search_clubs напрямую
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_consultant.services_v2 import AIConsultantServiceV2

print("=" * 60)
print("ТЕСТ search_clubs")
print("=" * 60)

service = AIConsultantServiceV2()

# Тест 1: Поиск по "танц"
print("\n1. Поиск по 'танц':")
result = service.get_clubs_by_interest_keywords("танц", 5)
print(f"Success: {result['success']}")
print(f"Type: {result.get('type')}")
print(f"Clubs found: {len(result.get('clubs', []))}")
for club in result.get('clubs', []):
    print(f"  - {club['name']} ({club['category']})")

# Тест 2: Форматирование
print("\n2. Форматированный ответ:")
formatted = service.format_club_recommendations(result)
print(formatted[:500])

print("\n" + "=" * 60)
print("ТЕСТ ЗАВЕРШЕН")
print("=" * 60)
