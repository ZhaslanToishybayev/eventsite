"""
Context Module for AI Consultant - анализирует сайт и дает контекст
"""
from clubs.models import Club, ClubCategory, City
from collections import Counter
import random


class SiteContext:
    """Класс для анализа контекста сайта"""

    @staticmethod
    def get_popular_categories():
        """Получаем популярные категории"""
        categories = ClubCategory.objects.filter(is_active=True)
        category_stats = []
        for category in categories:
            club_count = Club.objects.filter(category=category, is_active=True).count()
            category_stats.append({
                'name': category.name,
                'count': club_count,
                'popularity': 'high' if club_count > 3 else 'medium' if club_count > 1 else 'low'
            })
        return sorted(category_stats, key=lambda x: x['count'], reverse=True)

    @staticmethod
    def get_popular_cities():
        """Получаем популярные города"""
        cities = Club.objects.filter(is_active=True).values_list('city__name', flat=True)
        city_counts = Counter(cities)
        return city_counts.most_common(5)

    @staticmethod
    def get_trending_club_names():
        """Получаем популярные шаблоны названий"""
        clubs = Club.objects.filter(is_active=True).values_list('name', flat=True)
        name_patterns = {
            'academy': ['Академия', 'Академия', 'Школа'],
            'center': ['Центр', 'Центр', 'Клуб'],
            'pro': ['Про', 'Профессионалы', 'Эксперты'],
            'friends': ['Друзей', 'Любителей', 'Поклонников']
        }
        return name_patterns

    @staticmethod
    def get_category_examples(category_name):
        """Получаем примеры клубов по категории"""
        try:
            category = ClubCategory.objects.get(name=category_name, is_active=True)
            clubs = Club.objects.filter(category=category, is_active=True)[:3]
            return [club.name for club in clubs]
        except ClubCategory.DoesNotExist:
            return []

    @staticmethod
    def get_city_examples(city_name):
        """Получаем примеры клубов по городу"""
        clubs = Club.objects.filter(city__name__icontains=city_name, is_active=True)[:3]
        return [club.name for club in clubs]

    @staticmethod
    def generate_personalized_suggestions(user_message, category=None, city=None):
        """Генерируем персонализированные предложения"""
        suggestions = {}

        # Анализируем интересы пользователя из сообщения
        message_lower = user_message.lower()
        if any(word in message_lower for word in ['музыка', 'песня', 'песни']):
            suggestions['music'] = [
                "Молодежная Сцена",
                "Ритм-Тусовка",
                "Микрофон-Пати",
                "Звуковая Волна",
                "Мелодия Поколения"
            ]
        elif any(word in message_lower for word in ['спорт', 'игра', 'игры']):
            suggestions['sports'] = [
                "Спортивная Академия",
                "Чемпион-Клуб",
                "Тренажер-Тусовка",
                "Матч-Центр",
                "Фитнес-Френды"
            ]
        elif any(word in message_lower for word in ['игра', 'игровой', 'кибер']):
            suggestions['games'] = [
                "Игровая Площадка",
                "Кибер-Арена",
                "Геймер-Клуб",
                "Пиксель-Пати",
                "Лобби-Френды"
            ]

        # Добавляем локальные примеры
        if city:
            city_examples = SiteContext.get_city_examples(city)
            if city_examples:
                suggestions['local_examples'] = city_examples

        # Добавляем категорийные примеры
        if category:
            category_examples = SiteContext.get_category_examples(category)
            if category_examples:
                suggestions['category_examples'] = category_examples

        return suggestions


def get_site_context():
    """Получаем полный контекст сайта"""
    return {
        'popular_categories': SiteContext.get_popular_categories(),
        'popular_cities': SiteContext.get_popular_cities(),
        'trending_names': SiteContext.get_trending_club_names(),
        'total_clubs': Club.objects.filter(is_active=True).count(),
        'total_cities': City.objects.count()
    }