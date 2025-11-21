#!/usr/bin/env python
"""
Скрипт для инициализации категорий обратной связи
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_consultant.services.feedback import FeedbackService

def main():
    print("🚀 Инициализация категорий обратной связи...")

    feedback_service = FeedbackService()
    feedback_service.initialize_categories()

    print("✅ Категории обратной связи успешно инициализированы!")

if __name__ == '__main__':
    main()