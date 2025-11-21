#!/usr/bin/env python
"""
Скрипт для создания начальных данных для системы развития
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_consultant.models import (
    DevelopmentCategory,
    DevelopmentSkill,
    DevelopmentPath,
    DevelopmentResource
)

def create_development_categories():
    """Создает категории развития"""
    categories_data = [
        {
            'name': 'Бизнес и предпринимательство',
            'description': 'Навыки для создания и ведения бизнеса',
            'icon': '💼',
            'color': '#FF6B6B'
        },
        {
            'name': 'Технологии и программирование',
            'description': 'IT навыки и программирование',
            'icon': '💻',
            'color': '#4ECDC4'
        },
        {
            'name': 'Творчество и искусство',
            'description': 'Творческие навыки и искусство',
            'icon': '🎨',
            'color': '#45B7D1'
        },
        {
            'name': 'Личное развитие',
            'description': 'Личностный рост и саморазвитие',
            'icon': '🌱',
            'color': '#96CEB4'
        },
        {
            'name': 'Социальные навыки',
            'description': 'Коммуникация и работа с людьми',
            'icon': '👥',
            'color': '#FFEAA7'
        },
        {
            'name': 'Иностранные языки',
            'description': 'Изучение иностранных языков',
            'icon': '🌍',
            'color': '#DDA0DD'
        }
    ]

    for cat_data in categories_data:
        category, created = DevelopmentCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"✅ Создана категория: {category.name}")
        else:
            print(f"📝 Категория существует: {category.name}")

    return DevelopmentCategory.objects.all()

def create_development_skills(categories):
    """Создает навыки развития"""
    skills_data = [
        # Бизнес навыки
        {
            'category': categories[0],  # Бизнес
            'name': 'Основы предпринимательства',
            'description': 'Как начать свой бизнес с нуля',
            'difficulty_level': 1,
            'estimated_time': '1-2 месяца',
            'keywords': 'стартап, бизнес, идея, основы'
        },
        {
            'category': categories[0],  # Бизнес
            'name': 'Маркетинг и продажи',
            'description': 'Продвижение продуктов и услуг',
            'difficulty_level': 2,
            'estimated_time': '3-4 месяца',
            'keywords': 'маркетинг, продажи, клиенты, продвижение'
        },
        {
            'category': categories[0],  # Бизнес
            'name': 'Финансовая грамотность',
            'description': 'Управление личными и бизнес финансами',
            'difficulty_level': 2,
            'estimated_time': '2-3 месяца',
            'keywords': 'финансы, бюджет, инвестиции, деньги'
        },

        # Технологии
        {
            'category': categories[1],  # Технологии
            'name': 'Основы программирования на Python',
            'description': 'Первые шаги в программировании',
            'difficulty_level': 1,
            'estimated_time': '3-4 месяца',
            'keywords': 'python, программирование, код, разработка'
        },
        {
            'category': categories[1],  # Технологии
            'name': 'Веб-разработка',
            'description': 'Создание сайтов и веб-приложений',
            'difficulty_level': 2,
            'estimated_time': '4-6 месяцев',
            'keywords': 'веб, html, css, javascript, сайты'
        },
        {
            'category': categories[1],  # Технологии
            'name': 'Основы работы с данными',
            'description': 'Анализ и обработка данных',
            'difficulty_level': 3,
            'estimated_time': '6-8 месяцев',
            'keywords': 'данные, аналитика, sql, анализ'
        },

        # Творчество
        {
            'category': categories[2],  # Творчество
            'name': 'Основы рисования',
            'description': 'Техники рисования для начинающих',
            'difficulty_level': 1,
            'estimated_time': '2-3 месяца',
            'keywords': 'рисование, искусство, творчество'
        },
        {
            'category': categories[2],  # Творчество
            'name': 'Фотография для начинающих',
            'description': 'Основы композиции и техники фотографии',
            'difficulty_level': 1,
            'estimated_time': '1-2 месяца',
            'keywords': 'фотография, фото, камера, композиция'
        },
        {
            'category': categories[2],  # Творчество
            'name': 'Цифровой дизайн',
            'description': 'Создание графики в цифровых программах',
            'difficulty_level': 2,
            'estimated_time': '3-4 месяца',
            'keywords': 'дизайн, графика, photoshop, figma'
        },

        # Личное развитие
        {
            'category': categories[3],  # Личное развитие
            'name': 'Тайм-менеджмент',
            'description': 'Эффективное управление временем',
            'difficulty_level': 1,
            'estimated_time': '1 месяц',
            'keywords': 'время, планирование, продуктивность'
        },
        {
            'category': categories[3],  # Личное развитие
            'name': 'Эмоциональный интеллект',
            'description': 'Развитие эмоциональных навыков',
            'difficulty_level': 2,
            'estimated_time': '2-3 месяца',
            'keywords': 'эмоции, общение, самопознание'
        },
        {
            'category': categories[3],  # Личное развитие
            'name': 'Лидерские качества',
            'description': 'Развитие лидерских навыков',
            'difficulty_level': 3,
            'estimated_time': '4-6 месяцев',
            'keywords': 'лидерство, команда, управление'
        },

        # Социальные навыки
        {
            'category': categories[4],  # Социальные навыки
            'name': 'Публичные выступления',
            'description': 'Умение выступать перед аудиторией',
            'difficulty_level': 2,
            'estimated_time': '2-3 месяца',
            'keywords': 'выступления, аудитория, страх, оратор'
        },
        {
            'category': categories[4],  # Социальные навыки
            'name': 'Нетворкинг',
            'description': 'Построение профессиональных связей',
            'difficulty_level': 1,
            'estimated_time': '1 месяц',
            'keywords': 'нетворкинг, связи, знакомства, общение'
        },

        # Иностранные языки
        {
            'category': categories[5],  # Иностранные языки
            'name': 'Английский для начинающих',
            'description': 'Базовый уровень английского языка',
            'difficulty_level': 1,
            'estimated_time': '4-6 месяцев',
            'keywords': 'английский, english, beginner, начальный'
        },
        {
            'category': categories[5],  # Иностранные языки
            'name': 'Деловой английский',
            'description': 'Английский для делового общения',
            'difficulty_level': 2,
            'estimated_time': '3-4 месяца',
            'keywords': 'business english, деловой, профессиональный'
        }
    ]

    for skill_data in skills_data:
        skill, created = DevelopmentSkill.objects.get_or_create(
            name=skill_data['name'],
            category=skill_data['category'],
            defaults=skill_data
        )
        if created:
            print(f"✅ Создан навык: {skill.name}")
        else:
            print(f"📝 Навык существует: {skill.name}")

def create_development_paths(skills):
    """Создает дорожки развития"""
    paths_data = [
        {
            'title': 'Предприниматель с нуля',
            'description': 'Полный курс по созданию бизнеса для начинающих предпринимателей',
            'target_audience': 'Люди, которые хотят начать свой бизнес, но не знают с чего начать',
            'duration': '3-6 месяцев',
            'difficulty_level': 1,
            'is_recommended': True,
            'order': 1,
            'skills': skills.filter(name__in=['Основы предпринимательства', 'Маркетинг и продажи', 'Финансовая грамотность'])
        },
        {
            'title': 'Python разработчик',
            'description': 'Дорожка для становления Python разработчиком',
            'target_audience': 'Начинающие программисты и те, кто хочет сменить профессию',
            'duration': '6-8 месяцев',
            'difficulty_level': 1,
            'is_recommended': True,
            'order': 2,
            'skills': skills.filter(name__in=['Основы программирования на Python', 'Веб-разработка'])
        },
        {
            'title': 'Творческий предприниматель',
            'description': 'Развитие творческих навыков и их монетизация',
            'target_audience': 'Творческие люди, которые хотят превратить хобби в бизнес',
            'duration': '4-6 месяцев',
            'difficulty_level': 2,
            'is_recommended': True,
            'order': 3,
            'skills': skills.filter(name__in=['Основы рисования', 'Фотография для начинающих', 'Цифровой дизайн'])
        },
        {
            'title': 'Лидер будущего',
            'description': 'Развитие лидерских качеств и эмоционального интеллекта',
            'target_audience': 'Менеджеры, руководители и те, кто хочет стать лидером',
            'duration': '4-6 месяцев',
            'difficulty_level': 3,
            'is_recommended': True,
            'order': 4,
            'skills': skills.filter(name__in=['Эмоциональный интеллект', 'Лидерские качества', 'Публичные выступления'])
        }
    ]

    for path_data in paths_data:
        # Создаем дорожку без ManyToMany поля
        path_data_for_create = {
            'title': path_data['title'],
            'description': path_data['description'],
            'target_audience': path_data['target_audience'],
            'duration': path_data['duration'],
            'difficulty_level': path_data['difficulty_level'],
            'is_recommended': path_data['is_recommended'],
            'order': path_data['order'],
            'is_active': path_data.get('is_active', True)
        }

        path, created = DevelopmentPath.objects.get_or_create(
            title=path_data['title'],
            defaults=path_data_for_create
        )

        if created:
            path.skills.set(path_data['skills'])
            print(f"✅ Создана дорожка: {path.title}")
        else:
            print(f"📝 Дорожка существует: {path.title}")

def create_development_resources(skills):
    """Создает ресурсы для развития"""
    resources_data = [
        # Для Основ предпринимательства
        {
            'skill': skills.get(name='Основы предпринимательства'),
            'title': 'Бизнес с нуля (книга)',
            'description': 'Популярное руководство по созданию бизнеса',
            'resource_type': 'book',
            'url': 'https://example.com/business-book',
            'difficulty_level': 1,
            'estimated_time': '10 часов чтения',
            'is_recommended': True,
            'order': 1
        },
        {
            'skill': skills.get(name='Основы предпринимательства'),
            'title': 'Как найти бизнес-идею (видео)',
            'description': 'Практические методы поиска идей для бизнеса',
            'resource_type': 'video',
            'url': 'https://example.com/business-ideas',
            'difficulty_level': 1,
            'estimated_time': '45 минут',
            'is_free': True,
            'order': 2
        },

        # Для Python
        {
            'skill': skills.get(name='Основы программирования на Python'),
            'title': 'Python для начинающих (курс)',
            'description': 'Интерактивный курс изучения Python',
            'resource_type': 'course',
            'url': 'https://example.com/python-course',
            'difficulty_level': 1,
            'estimated_time': '30 часов',
            'is_recommended': True,
            'order': 1
        },
        {
            'skill': skills.get(name='Основы программирования на Python'),
            'title': 'Python документация',
            'description': 'Официальная документация Python',
            'resource_type': 'tool',
            'url': 'https://docs.python.org',
            'difficulty_level': 1,
            'estimated_time': 'Постоянно',
            'is_free': True,
            'order': 2
        },

        # Для Тайм-менеджмента
        {
            'skill': skills.get(name='Тайм-менеджмент'),
            'title': 'Метод Pomodoro (статья)',
            'description': 'Техника управления временем для повышения продуктивности',
            'resource_type': 'article',
            'url': 'https://example.com/pomodoro',
            'difficulty_level': 1,
            'estimated_time': '15 минут',
            'is_recommended': True,
            'order': 1
        },

        # Для Английского языка
        {
            'skill': skills.get(name='Английский для начинающих'),
            'title': 'Duolingo',
            'description': 'Бесплатное приложение для изучения языков',
            'resource_type': 'tool',
            'url': 'https://www.duolingo.com',
            'difficulty_level': 1,
            'estimated_time': '30 минут в день',
            'is_free': True,
            'is_recommended': True,
            'order': 1
        }
    ]

    for resource_data in resources_data:
        if resource_data['skill']:
            resource, created = DevelopmentResource.objects.get_or_create(
                title=resource_data['title'],
                skill=resource_data['skill'],
                defaults=resource_data
            )
            if created:
                print(f"✅ Создан ресурс: {resource.title}")
            else:
                print(f"📝 Ресурс существует: {resource.title}")

def main():
    print("🚀 Создание данных для системы развития...")

    print("\n1. Создание категорий...")
    categories = create_development_categories()

    print("\n2. Создание навыков...")
    create_development_skills(categories)

    print("\n3. Создание дорожек развития...")
    skills = DevelopmentSkill.objects.all()
    create_development_paths(skills)

    print("\n4. Создание ресурсов...")
    create_development_resources(skills)

    print("\n✅ Данные для системы развития успешно созданы!")

if __name__ == '__main__':
    main()