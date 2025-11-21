import re
from typing import List, Dict, Optional
from django.db.models import Q, Count, Case, When, IntegerField
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import (
    DevelopmentCategory,
    DevelopmentSkill,
    DevelopmentPath,
    UserDevelopmentPlan,
    UserSkillProgress,
    DevelopmentResource
)

User = get_user_model()


class DevelopmentRecommendationService:
    """
    Сервис для персональных рекомендаций по развитию
    """

    def __init__(self):
        self.development_keywords = {
            'бизнес': ['бизнес', 'предпринимательство', 'стартап', 'инвестиции', 'маркетинг', 'продажи', 'финансы', 'менеджмент'],
            'технологии': ['программирование', 'it', 'технологии', 'код', 'разработка', 'digital', 'ai', 'блокчейн'],
            'творчество': ['творчество', 'искусство', 'рисование', 'музыка', 'дизайн', 'фотография', 'писательство'],
            'личное развитие': ['развитие', 'саморазвитие', 'психология', 'мотивация', 'продуктивность', 'память', 'коммуникация'],
            'спорт': ['спорт', 'фитнес', 'здоровье', 'тренировки', 'йога', 'питание', 'медитация'],
            'иностранные языки': ['язык', 'английский', 'китайский', 'испанский', 'иностранный', 'перевод'],
            'образование': ['образование', 'обучение', 'курсы', 'учеба', 'знания', 'наука', 'исследования'],
            'социальные навыки': ['общение', 'социализация', 'лидерство', 'команда', 'переговоры', 'нетворкинг'],
            'финансы': ['финансы', 'инвестиции', 'бюджет', 'сбережения', 'криптовалюты', 'акции', 'банковское дело'],
            'маркетинг': ['маркетинг', 'реклама', 'seo', 'smm', 'контент', 'бренд', 'продвижение']
        }

    def analyze_user_development_needs(self, user: User, message: str = '') -> Dict[str, int]:
        """
        Анализирует потребности пользователя в развитии на основе профиля и сообщения
        """
        needs = {}

        # Анализируем профиль пользователя
        if hasattr(user, 'profile'):
            profile = user.profile
            text_to_analyze = []

            if profile.interests:
                text_to_analyze.append(profile.interests.lower())
            if profile.about:
                text_to_analyze.append(profile.about.lower())
            if profile.goals_for_life:
                text_to_analyze.append(profile.goals_for_life.lower())

            if message:
                text_to_analyze.append(message.lower())

            full_text = ' '.join(text_to_analyze)

            # Подсчет ключевых слов по категориям
            for category, keywords in self.development_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword in full_text:
                        score += full_text.count(keyword)
                if score > 0:
                    needs[category] = score

        return needs

    def get_development_paths_by_needs(self, needs: Dict[str, int], limit: int = 5) -> List[Dict]:
        """
        Находит дорожки развития на основе потребностей пользователя
        """
        if not needs:
            # Если потребности не определены, возвращаем рекомендуемые дорожки
            paths = DevelopmentPath.objects.filter(is_active=True, is_recommended=True)
        else:
            # Ищем дорожки по ключевым словам в названии и описании
            paths = DevelopmentPath.objects.filter(is_active=True)

        scored_paths = []

        for path in paths:
            score = self._calculate_path_score(path, needs)
            if score > 0:
                scored_paths.append({
                    'path': path,
                    'score': score,
                    'match_reasons': self._get_path_match_reasons(path, needs)
                })

        # Сортируем по релевантности
        scored_paths.sort(key=lambda x: x['score'], reverse=True)

        return scored_paths[:limit]

    def _calculate_path_score(self, path: DevelopmentPath, needs: Dict[str, int]) -> int:
        """
        Рассчитывает релевантность дорожки для пользователя
        """
        score = 0

        # Анализ текста дорожки
        path_text = ' '.join([
            path.title.lower(),
            path.description.lower(),
            path.target_audience.lower()
        ])

        # Проверяем совпадения по ключевым словам
        for category, user_score in needs.items():
            keywords = self.development_keywords[category]
            for keyword in keywords:
                if keyword in path_text:
                    score += user_score

        # Добавляем бонус за рекомендуемые дорожки
        if path.is_recommended:
            score += 10

        # Добавляем бонус за простые дорожки для начинающих
        if path.difficulty_level == 1:
            score += 5

        return score

    def _get_path_match_reasons(self, path: DevelopmentPath, needs: Dict[str, int]) -> List[str]:
        """
        Возвращает причины рекомендаций дорожки
        """
        reasons = []
        path_text = ' '.join([
            path.title.lower(),
            path.description.lower(),
            path.target_audience.lower()
        ])

        matched_categories = []
        for category, user_score in needs.items():
            keywords = self.development_keywords[category]
            for keyword in keywords:
                if keyword in path_text:
                    if category not in matched_categories:
                        matched_categories.append(category)
                        break

        if matched_categories:
            reasons.append(f"Совпадение интересов: {', '.join(matched_categories)}")

        if path.is_recommended:
            reasons.append("Рекомендуемая дорожка")

        if path.difficulty_level == 1:
            reasons.append("Отлично для начинающих")

        return reasons

    def get_skills_for_development(self, user: User, category: str = None, limit: int = 5) -> List[Dict]:
        """
        Получает рекомендации навыков для развития
        """
        skills = DevelopmentSkill.objects.filter(is_active=True)

        if category:
            try:
                dev_category = DevelopmentCategory.objects.get(name__iexact=category, is_active=True)
                skills = skills.filter(category=dev_category)
            except DevelopmentCategory.DoesNotExist:
                pass

        # Исключаем навыки, которые уже изучает пользователь
        user_progress_skills = UserSkillProgress.objects.filter(
            user=user,
            mastery_level__gte=1
        ).values_list('skill_id', flat=True)

        skills = skills.exclude(id__in=user_progress_skills)

        # Сортируем по сложности
        skills = skills.order_by('difficulty_level')[:limit]

        skill_list = []
        for skill in skills:
            skill_list.append({
                'id': str(skill.id),
                'name': skill.name,
                'description': skill.description,
                'category': skill.category.name,
                'difficulty_level': skill.difficulty_level,
                'estimated_time': skill.estimated_time,
                'keywords': skill.keywords
            })

        return skill_list

    def create_development_plan(self, user: User, path_id: str) -> Dict:
        """
        Создает план развития для пользователя
        """
        try:
            development_path = DevelopmentPath.objects.get(id=path_id, is_active=True)

            # Проверяем, нет ли уже такого плана
            existing_plan = UserDevelopmentPlan.objects.filter(
                user=user,
                development_path=development_path,
                is_active=True
            ).first()

            if existing_plan:
                return {
                    'success': False,
                    'error': 'У вас уже есть активный план по этой дорожке развития',
                    'plan_id': str(existing_plan.id)
                }

            # Создаем новый план
            plan = UserDevelopmentPlan.objects.create(
                user=user,
                development_path=development_path,
                progress_percentage=0
            )

            # Создаем записи о прогрессе для каждого навыка
            for skill in development_path.skills.all():
                UserSkillProgress.objects.get_or_create(
                    user=user,
                    skill=skill,
                    defaults={'mastery_level': 0}
                )

            return {
                'success': True,
                'plan_id': str(plan.id),
                'path_title': development_path.title,
                'duration': development_path.duration,
                'skills_count': development_path.skills.count()
            }

        except DevelopmentPath.DoesNotExist:
            return {
                'success': False,
                'error': 'Дорожка развития не найдена'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка создания плана: {str(e)}'
            }

    def get_user_development_progress(self, user: User) -> Dict:
        """
        Получает информацию о прогрессе развития пользователя
        """
        try:
            # Активные планы
            active_plans = UserDevelopmentPlan.objects.filter(
                user=user,
                is_active=True
            ).select_related('development_path')

            plans_data = []
            for plan in active_plans:
                # Получаем прогресс по навыкам
                skills_progress = UserSkillProgress.objects.filter(
                    user=user,
                    skill__in=plan.development_path.skills.all()
                ).select_related('skill')

                skills_data = []
                total_progress = 0
                skills_count = 0

                for progress in skills_progress:
                    skills_data.append({
                        'skill_name': progress.skill.name,
                        'skill_category': progress.skill.category.name,
                        'mastery_level': progress.mastery_level,
                        'practice_hours': progress.practice_hours,
                        'last_practiced': progress.last_practiced
                    })

                    total_progress += progress.mastery_level
                    skills_count += 1

                # Рассчитываем общий прогресс
                overall_progress = (total_progress / (skills_count * 4)) * 100 if skills_count > 0 else 0

                plans_data.append({
                    'plan_id': str(plan.id),
                    'path_title': plan.development_path.title,
                    'duration': plan.development_path.duration,
                    'overall_progress': round(overall_progress, 1),
                    'skills_count': skills_count,
                    'skills': skills_data,
                    'started_at': plan.started_at
                })

            return {
                'success': True,
                'plans': plans_data,
                'total_active_plans': len(plans_data)
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения прогресса: {str(e)}'
            }

    def get_development_resources(self, skill_id: str = None, user: User = None) -> List[Dict]:
        """
        Получает ресурсы для развития
        """
        resources = DevelopmentResource.objects.filter(is_active=True)

        if skill_id:
            resources = resources.filter(skill_id=skill_id)

        # Если пользователь авторизован, рекомендуем ресурсы по его уровню
        if user and hasattr(user, 'skill_progress'):
            user_levels = UserSkillProgress.objects.filter(user=user, mastery_level__gt=0)
            preferred_difficulty = 1  # Начинающий по умолчанию

            if user_levels.exists():
                avg_level = sum(p.mastery_level for p in user_levels) / len(user_levels)
                if avg_level >= 3:
                    preferred_difficulty = 3  # Продвинутый
                elif avg_level >= 2:
                    preferred_difficulty = 2  # Средний

            # Приоритет ресурсам подходящего уровня сложности
            resources = resources.annotate(
                priority=Case(
                    When(difficulty_level=preferred_difficulty, then=3),
                    When(difficulty_level=max(1, preferred_difficulty - 1), then=2),
                    default=1,
                    output_field=IntegerField(),
                )
            ).order_by('-priority', '-is_recommended', 'order')

        resource_list = []
        for resource in resources[:10]:  # Ограничиваем 10 ресурсами
            resource_list.append({
                'id': str(resource.id),
                'title': resource.title,
                'description': resource.description,
                'resource_type': resource.get_resource_type_display(),
                'url': resource.url,
                'difficulty_level': resource.difficulty_level,
                'estimated_time': resource.estimated_time,
                'is_free': resource.is_free,
                'is_recommended': resource.is_recommended,
                'skill_name': resource.skill.name,
                'skill_category': resource.skill.category.name
            })

        return resource_list

    def get_development_recommendations(self, user: User, message: str = '') -> Dict:
        """
        Основной метод для получения персональных рекомендаций по развитию
        """
        try:
            # Анализируем потребности пользователя
            needs = self.analyze_user_development_needs(user, message)

            # Получаем дорожки развития
            paths = self.get_development_paths_by_needs(needs, limit=3)

            # Получаем текущие планы пользователя
            current_progress = self.get_user_development_progress(user)

            # Получаем рекомендации навыков
            skills = self.get_skills_for_development(user, limit=5)

            # Получаем ресурсы
            resources = self.get_development_resources(user=user)

            return {
                'success': True,
                'development_needs': needs,
                'recommended_paths': paths,
                'current_progress': current_progress,
                'recommended_skills': skills,
                'recommended_resources': resources
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения рекомендаций: {str(e)}'
            }

    def format_development_recommendations(self, recommendations_data: Dict) -> str:
        """
        Форматирует рекомендации по развитию для ответа ИИ
        """
        if not recommendations_data['success']:
            return "К сожалению, я не смог получить рекомендации по развитию. Попробуйте описать, какие навыки вы хотели бы развивать."

        response = "📈 **Персональные рекомендации по развитию:**\n\n"

        # Добавляем информацию о текущих планах
        if recommendations_data['current_progress']['total_active_plans'] > 0:
            response += "🎯 **Ваши текущие планы развития:**\n"
            for plan in recommendations_data['current_progress']['plans']:
                response += f"• **{plan['path_title']}** - {plan['overall_progress']}% прогресса\n"
            response += "\n"

        # Добавляем рекомендуемые дорожки
        if recommendations_data['recommended_paths']:
            response += "🛤️ **Рекомендуемые дорожки развития:**\n"
            for i, path_data in enumerate(recommendations_data['recommended_paths'][:3], 1):
                path = path_data['path']
                response += f"\n**{i}. {path.title}**\n"
                response += f"📝 {path.description[:100]}...\n"
                response += f"⏱️ Продолжительность: {path.duration}\n"
                response += f"👥 Для: {path.target_audience[:50]}...\n"

                if path_data['match_reasons']:
                    response += f"✨ Почему рекомендую: {', '.join(path_data['match_reasons'])}\n"

            response += "\n"

        # Добавляем навыки для развития
        if recommendations_data['recommended_skills']:
            response += "🎯 **Навыки, которые можно развить:**\n"
            for skill in recommendations_data['recommended_skills'][:3]:
                response += f"• **{skill['name']}** ({skill['category']}) - {skill['estimated_time']}\n"
            response += "\n"

        # Добавляем полезные ресурсы
        if recommendations_data['recommended_resources']:
            response += "📚 **Полезные ресурсы:**\n"
            for resource in recommendations_data['recommended_resources'][:3]:
                emoji = "📖" if resource['resource_type'] == 'Книга' else "🎥" if resource['resource_type'] == 'Видео' else "📄"
                response += f"{emoji} **{resource['title']}** ({resource['resource_type']})\n"
            response += "\n"

        # Добавляем призыв к действию
        response += "💡 **Хотите начать какой-то план развития или узнать подробнее о ресурсах?**"

        return response