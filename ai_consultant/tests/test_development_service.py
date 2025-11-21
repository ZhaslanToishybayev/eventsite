import pytest
from unittest.mock import MagicMock
from django.contrib.auth import get_user_model
from ai_consultant.services.development import DevelopmentRecommendationService
from ai_consultant.models import (
    DevelopmentCategory,
    DevelopmentSkill,
    DevelopmentPath,
    UserDevelopmentPlan,
    UserSkillProgress,
    DevelopmentResource
)

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create_user(phone='+77012345678', password='password', email='test@example.com')

@pytest.fixture
def dev_category():
    return DevelopmentCategory.objects.create(
        name='Программирование',
        description='Навыки программирования',
        is_active=True
    )

@pytest.fixture
def dev_skill(dev_category):
    return DevelopmentSkill.objects.create(
        name='Python',
        description='Язык программирования Python',
        category=dev_category,
        difficulty_level=2,
        estimated_time='3 месяца',
        is_active=True
    )

@pytest.fixture
def dev_path(dev_category, dev_skill):
    path = DevelopmentPath.objects.create(
        title='Путь Python разработчика',
        description='Станьте профессиональным Python разработчиком',
        difficulty_level=2,
        duration='6 месяцев',
        target_audience='Начинающие разработчики',
        is_active=True,
        is_recommended=True
    )
    path.skills.add(dev_skill)
    return path

@pytest.fixture
def development_service():
    return DevelopmentRecommendationService()

@pytest.mark.django_db
class TestDevelopmentRecommendationService:

    def test_analyze_user_development_needs(self, development_service, user):
        # Create profile with development interests
        from accounts.models import Profile
        Profile.objects.create(
            user=user,
            interests='программирование python разработка',
            about='Хочу стать разработчиком',
            goals_for_life='Создать свой стартап'
        )
        
        needs = development_service.analyze_user_development_needs(user, 'хочу изучить python')
        
        assert 'технологии' in needs
        assert needs['технологии'] > 0

    def test_get_development_paths_by_needs(self, development_service, dev_path):
        needs = {'технологии': 5}
        
        paths = development_service.get_development_paths_by_needs(needs, limit=5)
        
        assert len(paths) > 0
        assert paths[0]['path'] == dev_path

    def test_create_development_plan(self, development_service, user, dev_path):
        result = development_service.create_development_plan(user, str(dev_path.id))
        
        assert result['success'] is True
        assert 'plan_id' in result
        assert result['path_title'] == dev_path.title

    def test_create_development_plan_duplicate(self, development_service, user, dev_path):
        # Create first plan
        development_service.create_development_plan(user, str(dev_path.id))
        
        # Try to create duplicate
        result = development_service.create_development_plan(user, str(dev_path.id))
        
        assert result['success'] is False
        assert 'уже есть активный план' in result['error']

    def test_get_user_development_progress(self, development_service, user, dev_path, dev_skill):
        # Create plan
        plan = UserDevelopmentPlan.objects.create(
            user=user,
            development_path=dev_path,
            progress_percentage=0
        )
        
        # Create skill progress
        UserSkillProgress.objects.create(
            user=user,
            skill=dev_skill,
            mastery_level=2,
            practice_hours=10
        )
        
        result = development_service.get_user_development_progress(user)
        
        assert result['success'] is True
        assert result['total_active_plans'] == 1
        assert len(result['plans']) == 1
        assert result['plans'][0]['path_title'] == dev_path.title

    def test_get_skills_for_development(self, development_service, user, dev_skill):
        skills = development_service.get_skills_for_development(user, limit=5)
        
        assert len(skills) > 0
        assert skills[0]['name'] == dev_skill.name

    def test_get_skills_for_development_excludes_user_skills(self, development_service, user, dev_skill):
        # User already learning this skill
        UserSkillProgress.objects.create(
            user=user,
            skill=dev_skill,
            mastery_level=2
        )
        
        skills = development_service.get_skills_for_development(user, limit=5)
        
        # Should not include the skill user is already learning
        skill_names = [s['name'] for s in skills]
        assert dev_skill.name not in skill_names

    def test_get_development_recommendations(self, development_service, user, dev_path):
        # Create profile
        from accounts.models import Profile
        Profile.objects.create(
            user=user,
            interests='программирование python'
        )
        
        result = development_service.get_development_recommendations(user, 'хочу изучить python')
        
        assert result['success'] is True
        assert 'recommended_paths' in result
        assert 'recommended_skills' in result
        assert 'current_progress' in result

    def test_format_development_recommendations(self, development_service):
        recommendations_data = {
            'success': True,
            'development_needs': {'технологии': 5},
            'recommended_paths': [],
            'current_progress': {'total_active_plans': 0, 'plans': []},
            'recommended_skills': [],
            'recommended_resources': []
        }
        
        formatted = development_service.format_development_recommendations(recommendations_data)
        
        assert '📈' in formatted
        assert 'Персональные рекомендации' in formatted
