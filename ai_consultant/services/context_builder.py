from typing import Dict, Any, List
from django.contrib.auth import get_user_model
from django.utils import timezone
from clubs.models import Club, ClubCategory
from ..models import ChatSession, ChatMessage

User = get_user_model()

class ContextBuilder:
    """
    Сервис для построения расширенного контекста пользователя
    """
    
    def build_user_context(self, user: User) -> str:
        """
        Строит текстовое представление контекста пользователя для промпта
        """
        context_parts = []
        
        # 1. Профиль пользователя
        profile_info = self._get_profile_info(user)
        if profile_info:
            context_parts.append(f"👤 ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ:\n{profile_info}")
            
        # 2. Интересы
        interests = self._get_user_interests(user)
        if interests:
            context_parts.append(f"❤️ ИНТЕРЕСЫ:\n{interests}")
            
        # 3. Клубы
        clubs = self._get_user_clubs(user)
        if clubs:
            context_parts.append(f"🏰 КЛУБЫ:\n{clubs}")
            
        # 4. Последняя активность
        activity = self._get_recent_activity(user)
        if activity:
            context_parts.append(f"🕒 АКТИВНОСТЬ:\n{activity}")
            
        return "\n\n".join(context_parts)
    
    def _get_profile_info(self, user: User) -> str:
        """Получение информации из профиля"""
        info = [f"Имя: {user.first_name} {user.last_name}"]
        
        # Если есть связанный профиль (предполагаем наличие модели Profile)
        if hasattr(user, 'profile'):
            profile = user.profile
            if hasattr(profile, 'about') and profile.about:
                info.append(f"О себе: {profile.about}")
            if hasattr(profile, 'city') and profile.city:
                info.append(f"Город: {profile.city}")
                
        return "\n".join(info)
    
    def _get_user_interests(self, user: User) -> str:
        """Получение интересов пользователя"""
        if hasattr(user, 'profile') and hasattr(user.profile, 'interests'):
            return user.profile.interests
        return ""
    
    def _get_user_clubs(self, user: User) -> str:
        """Получение клубов пользователя"""
        # Клубы, где пользователь участник
        member_clubs = Club.objects.filter(participants=user).values_list('title', flat=True)[:5]
        
        # Клубы, созданные пользователем
        created_clubs = Club.objects.filter(creater=user).values_list('title', flat=True)[:3]
        
        info = []
        if member_clubs:
            info.append(f"Участник: {', '.join(member_clubs)}")
        if created_clubs:
            info.append(f"Создатель: {', '.join(created_clubs)}")
            
        return "\n".join(info)
        
    def _get_recent_activity(self, user: User) -> str:
        """Получение последней активности в чате"""
        last_session = ChatSession.objects.filter(user=user).order_by('-updated_at').first()
        if last_session:
            days_ago = (timezone.now() - last_session.updated_at).days
            if days_ago == 0:
                return "Был активен сегодня"
            return f"Был активен {days_ago} дн. назад"
        return "Новый пользователь"
