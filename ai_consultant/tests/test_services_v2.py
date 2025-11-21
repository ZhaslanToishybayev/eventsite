import pytest
from unittest.mock import MagicMock, patch
from django.contrib.auth import get_user_model
from ai_consultant.services_v2 import AIConsultantServiceV2
from ai_consultant.models import ChatSession

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create_user(phone='+77012345678', password='password', email='test@example.com')

@pytest.fixture
def ai_service():
    # Mock dependencies
    with patch('ai_consultant.services_v2.ChatService') as MockChatService, \
         patch('ai_consultant.services_v2.ContextService') as MockContextService, \
         patch('ai_consultant.services_v2.MessageProcessorService') as MockMessageProcessorService, \
         patch('ai_consultant.services_v2.ClubCreationService') as MockClubCreationService, \
         patch('ai_consultant.services_v2.FeedbackService') as MockFeedbackService, \
         patch('ai_consultant.services_v2.PlatformServiceManager') as MockPlatformServiceManager, \
         patch('ai_consultant.services_v2.InterviewStudioService') as MockInterviewStudioService, \
         patch('ai_consultant.services_v2.ClubRecommendationService') as MockClubRecommendationService, \
         patch('ai_consultant.services_v2.DevelopmentRecommendationService') as MockDevelopmentRecommendationService, \
         patch('ai_consultant.services_v2.OpenAIClientService') as MockOpenAIClientService:
        
        service = AIConsultantServiceV2()
        return service

@pytest.mark.django_db
class TestAIConsultantServiceV2:

    def test_create_chat_session(self, ai_service, user):
        ai_service.chat_service.create_session.return_value = ChatSession(id=1, user=user)
        session = ai_service.create_chat_session(user)
        assert session.user == user
        ai_service.chat_service.create_session.assert_called_once_with(user)

    def test_get_club_recommendations_for_user_personalized(self, ai_service, user):
        # Mock personalized recommendations
        mock_club = MagicMock()
        mock_club.id = 1
        mock_club.name = "Test Club"
        mock_club.description = "Description"
        mock_club.category.name = "Category"
        mock_club.members_count = 10
        
        ai_service.recommendation_service.get_club_recommendations_for_user.return_value = [
            {'club': mock_club, 'match_reasons': ['Reason 1']}
        ]

        result = ai_service.get_club_recommendations_for_user(user)

        assert result['success'] is True
        assert result['type'] == 'personalized'
        assert len(result['clubs']) == 1
        assert result['clubs'][0]['name'] == "Test Club"
        ai_service.recommendation_service.get_club_recommendations_for_user.assert_called_once_with(user, 5)

    def test_get_club_recommendations_for_user_popular(self, ai_service, user):
        # Mock no personalized recommendations, fallback to popular
        ai_service.recommendation_service.get_club_recommendations_for_user.return_value = []
        
        mock_club = MagicMock()
        mock_club.id = 2
        mock_club.name = "Popular Club"
        mock_club.description = "Description"
        mock_club.category.name = "Category"
        mock_club.members_count = 100
        
        ai_service.recommendation_service.get_popular_clubs.return_value = [mock_club]

        result = ai_service.get_club_recommendations_for_user(user)

        assert result['success'] is True
        assert result['type'] == 'popular'
        assert len(result['clubs']) == 1
        assert result['clubs'][0]['name'] == "Popular Club"
        ai_service.recommendation_service.get_popular_clubs.assert_called_once_with(5)

    def test_get_clubs_by_interest_keywords_interests_found(self, ai_service):
        # Mock interests analysis found
        ai_service.recommendation_service.analyze_user_interests.return_value = ['coding']
        
        mock_club = MagicMock()
        mock_club.id = 3
        mock_club.name = "Coding Club"
        mock_club.description = "Description"
        mock_club.category.name = "Tech"
        mock_club.members_count = 50
        
        ai_service.recommendation_service.find_clubs_by_interests.return_value = [
            {'club': mock_club, 'match_reasons': ['Matches coding']}
        ]

        result = ai_service.get_clubs_by_interest_keywords("I like coding")

        assert result['success'] is True
        assert result['type'] == 'interest_based'
        assert len(result['clubs']) == 1
        assert result['clubs'][0]['name'] == "Coding Club"
        ai_service.recommendation_service.analyze_user_interests.assert_called_once()

    def test_create_interview_request(self, ai_service, user):
        data = {'details': 'Test request'}
        ai_service.interview_studio_service.create_interview_request.return_value = {'success': True}
        
        result = ai_service.create_interview_request(user, data)
        
        assert result['success'] is True
        ai_service.interview_studio_service.create_interview_request.assert_called_once_with(user, data)

    def test_get_development_recommendations_for_user(self, ai_service, user):
        ai_service.development_service.get_development_recommendations.return_value = {'success': True}
        
        result = ai_service.get_development_recommendations_for_user(user, "message")
        
        assert result['success'] is True
        ai_service.development_service.get_development_recommendations.assert_called_once_with(user, "message")

    def test_get_user_development_progress(self, ai_service, user):
        ai_service.development_service.get_user_development_progress.return_value = {'progress': 50}
        
        result = ai_service.get_user_development_progress(user)
        
        assert result['progress'] == 50
        ai_service.development_service.get_user_development_progress.assert_called_once_with(user)

    def test_create_development_plan_for_user(self, ai_service, user):
        ai_service.development_service.create_development_plan.return_value = {'success': True}
        
        result = ai_service.create_development_plan_for_user(user, "path_id")
        
        assert result['success'] is True
        ai_service.development_service.create_development_plan.assert_called_once_with(user, "path_id")

    def test_get_user_sessions(self, ai_service, user):
        ai_service.chat_service.get_user_sessions.return_value = [{'id': 1}]
        
        result = ai_service.get_user_sessions(user)
        
        assert len(result) == 1
        assert result[0]['id'] == 1
        ai_service.chat_service.get_user_sessions.assert_called_once_with(user)
