import pytest
from unittest.mock import MagicMock, patch
from django.contrib.auth import get_user_model
from clubs.services import ClubRecommendationService
from clubs.models import Club, ClubCategory

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create_user(phone='+77012345678', password='password', email='test@example.com')

@pytest.fixture
def club_category():
    return ClubCategory.objects.create(name='Технологии', is_active=True)

@pytest.fixture
def club(club_category, user):
    return Club.objects.create(
        name='Python Developers',
        description='Клуб для разработчиков на Python',
        category=club_category,
        creater=user,
        is_active=True,
        is_private=False,
        members_count=50,
        likes_count=20
    )

@pytest.fixture
def recommendation_service():
    return ClubRecommendationService()

@pytest.mark.django_db
class TestClubRecommendationService:

    def test_analyze_user_interests(self, recommendation_service, user):
        # Create profile with interests
        from accounts.models import Profile
        Profile.objects.create(
            user=user,
            interests='программирование python разработка',
            about='Я разработчик',
            goals_for_life='Стать лучшим программистом'
        )
        
        interests = recommendation_service.analyze_user_interests(user)
        
        assert 'технологии' in interests
        assert interests['технологии'] > 0

    def test_get_popular_clubs(self, recommendation_service, club):
        popular_clubs = recommendation_service.get_popular_clubs(limit=5)
        
        assert len(popular_clubs) > 0
        assert club in popular_clubs

    def test_get_clubs_by_category(self, recommendation_service, club, club_category):
        clubs = recommendation_service.get_clubs_by_category('Технологии', limit=10)
        
        assert len(clubs) > 0
        assert club in clubs

    def test_get_featured_clubs(self, recommendation_service, club_category, user):
        # Create featured club
        featured_club = Club.objects.create(
            name='Featured Club',
            description='This is a featured club',
            category=club_category,
            creater=user,
            is_active=True,
            is_private=False,
            is_featured=True,
            members_count=100
        )
        
        featured_clubs = recommendation_service.get_featured_clubs(limit=5)
        
        assert len(featured_clubs) > 0
        assert featured_club in featured_clubs

    def test_get_club_recommendations_for_user_excludes_user_clubs(self, recommendation_service, user, club):
        # Add user to club
        club.members.add(user)
        
        # Create profile with interests
        from accounts.models import Profile
        Profile.objects.create(
            user=user,
            interests='программирование python',
        )
        
        recommendations = recommendation_service.get_club_recommendations_for_user(user, limit=10)
        
        # User's club should be excluded
        recommended_clubs = [rec['club'] for rec in recommendations]
        assert club not in recommended_clubs
