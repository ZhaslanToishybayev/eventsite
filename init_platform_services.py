#!/usr/bin/env python
"""
Скрипт для инициализации услуг платформы
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_consultant.services.platform import PlatformServiceManager

def main():
    print("🚀 Инициализация услуг платформы...")

    service_manager = PlatformServiceManager()
    service_manager.initialize_services()

    print("✅ Услуги платформы успешно инициализированы!")

if __name__ == '__main__':
    main()