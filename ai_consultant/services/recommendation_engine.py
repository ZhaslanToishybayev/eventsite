from typing import List, Dict, Any
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from clubs.models import Club, ClubCategory

User = get_user_model()

class RecommendationEngine:
    """
    Движок рекомендаций для AI консультанта
    """
    
    def get_smart_recommendations(self, user: User, context_data: Dict = None) -> List[Dict[str, Any]]:
        """
        Получает умные рекомендации на основе профиля и активности
        """
        recommendations = []
        
        # 1. Рекомендации клубов
        club_recs = self._get_club_recommendations(user)
        recommendations.extend(club_recs)
        
        # 2. Рекомендации событий (заглушка, если нет модели Event)
        # event_recs = self._get_event_recommendations(user)
        # recommendations.extend(event_recs)
        
        # 3. Ранжирование смешанных рекомендаций
        ranked_recs = self._rank_recommendations(recommendations, user)
        
        return ranked_recs[:5]
        
    def _get_club_recommendations(self, user: User) -> List[Dict[str, Any]]:
        """Получение рекомендаций клубов"""
        recs = []
        
        # Исключаем клубы, где пользователь уже участник
        user_clubs = Club.objects.filter(participants=user)
        
        # Находим популярные клубы
        popular_clubs = Club.objects.exclude(
            id__in=user_clubs.values('id')
        ).annotate(
            members_count=Count('participants')
        ).order_by('-members_count')[:5]
        
        for club in popular_clubs:
            recs.append({
                'type': 'club',
                'id': club.id,
                'title': club.title,
                'score': 0.8,  # Базовый скор популярности
                'reason': 'Популярно в сообществе'
            })
            
        return recs
        
    def _rank_recommendations(self, recommendations: List[Dict[str, Any]], user: User) -> List[Dict[str, Any]]:
        """
        Ранжирование рекомендаций
        """
        # Здесь можно добавить логику ML или сложных правил
        # Пока просто сортируем по score
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)
