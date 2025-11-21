from . import models



class ClubServices:
    """
    Предоставляет методы для управления действиями относящихся клубу.
    """
    @staticmethod
    def join(club, user):
        """
        Добавляет пользователя в члены клуба и обновляет количество участников.

        Args:
            club (Club): Клуб, в который хочет вступить пользователь.
            user (User): Пользователь, который хочет вступить в клуб.

        Raises:
            clubs_exceptions.UserAlreadyInClubException: Если пользователь уже является членом клуба.
        """
        from clubs.api import exceptions as clubs_exceptions
        if club.members.filter(id=user.id).exists():
            raise clubs_exceptions.UserAlreadyInClubException
        if club.is_private:
            if models.ClubJoinRequest.objects.filter(user=user, club=club).exists():
                raise clubs_exceptions.ClubJoinRequestAlreadyExistsException
            models.ClubJoinRequest.objects.create(club=club, user=user)
        else:
            club.members.add(user)
            club.members_count += 1
            club.save()

    @staticmethod
    def leave(club, user):
        """
        Удаляет пользователя из членов клуба и обновляет количество участников.

        Args:
            club (Club): Клуб, который хочет покинуть пользователь.
            user (User): Пользователь, который хочет покинуть клуб.

        Raises:
            clubs_exceptions.UserNotInClubException: Если пользователь не является членом клуба.
        """
        from clubs.api import exceptions as clubs_exceptions
        if not club.members.filter(id=user.id).exists():
            raise clubs_exceptions.UserNotInClubException
        club.members.remove(user)
        club.members_count -= 1
        club.save()

    @staticmethod
    def like(club, user):
        """
        Добавляет пользователя в лайкнувшие клуб и обновляет количество лайков.

        Args:
            club (Club): Клуб, который хочет лайкнуть пользователь.
            user (User): Пользователь, который хочет лайкнуть клуб.

        Raises:
            clubs_exceptions.UserLikeAlreadyExistsException: Если пользователь уже лайкнул клуб.
        """
        from clubs.api import exceptions as clubs_exceptions
        if club.likes.filter(id=user.id).exists():
            raise clubs_exceptions.UserLikeAlreadyExistsException
        club.likes.add(user)
        club.likes_count += 1
        club.save()

    @staticmethod
    def unlike(club, user):
        """
        Удаляет пользователя из лайкнувших клуб и обновляет количество лайков.

        Args:
            club (Club): Клуб, у которого хочет удалить свой лайк пользователь.
            user (User): Пользователь, который хочет удалить свой лайк из клуба.

        Raises:
            clubs_exceptions.UserLikeDoesNotExistException: Если пользователь не лайкнул клуб.
        """
        from clubs.api import exceptions as clubs_exceptions
        if not club.likes.filter(id=user.id).exists():
            raise clubs_exceptions.UserLikeDoesNotExistException
        club.likes.remove(user)
        club.likes_count -= 1
        club.save()


class ClubJoinRequestServices:
    @staticmethod
    def approve(request: models.ClubJoinRequest):
        request.approved = True
        request.save()
        request.club.members.add(request.user)

    @staticmethod
    def reject(request: models.ClubJoinRequest):
        request.approved = False
        request.save()


class ClubPartnershipRequestServices:

    @staticmethod
    def approve(request: models.ClubPartnerShipRequest) -> None:
        request.approved = True
        request.save()
        request.club_accepter.partners.add(request.club_requester)

    @staticmethod
    def reject(request: models.ClubPartnerShipRequest) -> None:
        request.approved = False
        request.save()


class FestivalServices:
    """
    Класс FestivalServices предоставляет статические методы для управления участием клубов в фестивалях.
    """

    @staticmethod
    def join(festival: models.Festival, club: models.Club):
        """
        Отправляет запрос на участие клуба в фестивале.

        Args:
            festival (models.Festival): Фестиваль, в который клуб хочет присоединиться.
            club (models.Club): Клуб, который хочет присоединиться к фестивалю.

        Raises:
            exceptions.ClubAlreadyExistsFestivalException: Если клуб уже участвует в фестивале.
            exceptions.FestivalRequestAlreadyExistsException: Если у клуба уже есть заявка на участие в фестивале.
        """
        from clubs.api import exceptions as clubs_exceptions
        from clubs.api import exceptions as clubs_exceptions
        if festival.approved_clubs.filter(id=club.id).exists():
            raise clubs_exceptions.ClubAlreadyExistsFestivalException
        if models.FestivalParticipationRequest.objects.filter(festival=festival, club=club).exists():
            raise clubs_exceptions.FestivalRequestAlreadyExistsException
        models.FestivalParticipationRequest.objects.create(club=club, festival=festival)

    @staticmethod
    def leave(festival: models.Festival, club: models.Club):
        """
        Удаляет клуб из фестиваля.

        Args:
            festival (models.Festival): Фестиваль, из которого клуб хочет выйти.
            club (models.Club): Клуб, который хочет выйти из фестиваля.

        Raises:
            exceptions.ClubNotExistsFestivalException: Если клуб не участвует в фестивале.
        """
        from clubs.api import exceptions as clubs_exceptions
        if not festival.approved_clubs.filter(id=club.id).exists():
            raise clubs_exceptions.ClubNotExistsFestivalException
        festival.approved_clubs.remove(club)


class FestivalRequestServices:

    @staticmethod
    def approve(request: models.FestivalParticipationRequest):
        """
        Одобряет запрос на участие клуба в фестивале.

        Args:
            request: Запрос на вступление фестиваль.
        """
        request.approved = True
        request.save()
        request.festival.approved_clubs.add(request.club)

    @staticmethod
    def reject(request: models.FestivalParticipationRequest):
        """
        Отклоняет запрос на участие клуба в фестивале.

        Args:
            request: Запрос на вступление фестиваль.
        """
        request.approved = False
        request.festival.approved_clubs.remove(request.club)
        request.save()


import re
from typing import List, Dict, Optional
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from .models import Club, ClubCategory

User = get_user_model()


class ClubRecommendationService:
    """
    Сервис для рекомендаций клубов на основе интересов пользователей
    """

    def __init__(self):
        self.interest_keywords = {
            'спорт': ['спорт', 'футбол', 'бег', 'фитнес', 'тренировка', 'здоровье', 'активный', 'движение'],
            'технологии': ['технологии', 'программирование', 'it', 'компьютер', 'код', 'разработка', 'digital'],
            'творчество': ['творчество', 'искусство', 'рисование', 'музыка', 'танцы', 'дизайн', 'фотография'],
            'бизнес': ['бизнес', 'предпринимательство', 'стартап', 'инвестиции', 'маркетинг', 'продажи'],
            'образование': ['образование', 'обучение', 'курсы', 'школа', 'университет', 'наука', 'знания'],
            'социальная деятельность': ['волонтерство', 'помощь', 'благотворительность', 'социальный', 'общество'],
            'хобби': ['хобби', 'увлечения', 'рукоделие', 'коллекционирование', 'игры', 'книги'],
            'развитие': ['развитие', 'личностный рост', 'саморазвитие', 'психология', 'мотивация'],
            'туризм': ['путешествия', 'туризм', 'природа', 'походы', 'альпинизм', 'исследования'],
            'культура': ['культура', 'театр', 'кино', 'литература', 'история', 'языки']
        }

    def analyze_user_interests(self, user: User) -> Dict[str, int]:
        """
        Анализирует интересы пользователя на основе профиля и активности
        """
        interests = {}

        # Анализ профиля пользователя
        if hasattr(user, 'profile'):
            profile = user.profile
            text_to_analyze = []

            if profile.interests:
                text_to_analyze.append(profile.interests.lower())
            if profile.about:
                text_to_analyze.append(profile.about.lower())
            if profile.goals_for_life:
                text_to_analyze.append(profile.goals_for_life.lower())

            full_text = ' '.join(text_to_analyze)

            # Подсчет ключевых слов
            for category, keywords in self.interest_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword in full_text:
                        score += full_text.count(keyword)
                if score > 0:
                    interests[category] = score

        return interests

    def find_clubs_by_interests(self, interests: Dict[str, int], limit: int = 10) -> List[Dict]:
        """
        Находит клубы по интересам пользователя
        """
        if not interests:
            return []

        clubs = Club.objects.filter(is_active=True, is_private=False)

        scored_clubs = []

        for club in clubs:
            score = self._calculate_club_score(club, interests)
            if score > 0:
                scored_clubs.append({
                    'club': club,
                    'score': score,
                    'match_reasons': self._get_match_reasons(club, interests)
                })

        # Сортируем по релевантности
        scored_clubs.sort(key=lambda x: x['score'], reverse=True)

        return scored_clubs[:limit]

    def _calculate_club_score(self, club: Club, interests: Dict[str, int]) -> int:
        """
        Рассчитывает релевантность клуба для пользователя
        """
        score = 0

        # Анализ текста клуба
        club_text = ' '.join([
            club.name.lower(),
            club.description.lower(),
            club.tags.lower() if club.tags else '',
            club.target_audience.lower() if club.target_audience else '',
            club.activities.lower() if club.activities else '',
            club.skills_developed.lower() if club.skills_developed else ''
        ])

        # Проверяем совпадения по ключевым словам
        for category, user_score in interests.items():
            keywords = self.interest_keywords[category]
            for keyword in keywords:
                if keyword in club_text:
                    score += user_score

        # Добавляем бонус за фичерные клубы
        if club.is_featured:
            score += 10

        # Добавляем бонус за популярность
        score += min(club.members_count // 10, 5)
        score += min(club.likes_count // 10, 3)

        # Добавляем рекомендационный скор
        score += club.recommendation_score

        return score

    def _get_match_reasons(self, club: Club, interests: Dict[str, int]) -> List[str]:
        """
        Возвращает причины рекомендаций клуба
        """
        reasons = []
        club_text = ' '.join([
            club.name.lower(),
            club.description.lower(),
            club.tags.lower() if club.tags else '',
            club.target_audience.lower() if club.target_audience else '',
            club.activities.lower() if club.activities else '',
            club.skills_developed.lower() if club.skills_developed else ''
        ])

        matched_categories = []
        for category, user_score in interests.items():
            keywords = self.interest_keywords[category]
            for keyword in keywords:
                if keyword in club_text:
                    if category not in matched_categories:
                        matched_categories.append(category)
                        break

        if matched_categories:
            reasons.append(f"Совпадение интересов: {', '.join(matched_categories)}")

        if club.is_featured:
            reasons.append("Рекомендуемый клуб")

        if club.members_count > 50:
            reasons.append(f"Активное сообщество ({club.members_count} участников)")

        if club.skills_developed:
            reasons.append("Развивает полезные навыки")

        return reasons

    def get_club_recommendations_for_user(self, user: User, limit: int = 10) -> List[Dict]:
        """
        Получает рекомендации клубов для конкретного пользователя
        """
        # Исключаем клубы, в которых пользователь уже состоит
        user_clubs = user.members_of_clubs.all() if hasattr(user, 'members_of_clubs') else []
        user_club_ids = [club.id for club in user_clubs]

        # Анализируем интересы
        interests = self.analyze_user_interests(user)

        # Находим подходящие клубы
        recommendations = self.find_clubs_by_interests(interests, limit * 2)

        # Исключаем уже существующие клубы
        filtered_recommendations = [
            rec for rec in recommendations
            if rec['club'].id not in user_club_ids
        ]

        return filtered_recommendations[:limit]

    def get_similar_clubs(self, club: Club, limit: int = 5) -> List[Club]:
        """
        Находит похожие клубы
        """
        similar_clubs = Club.objects.filter(
            is_active=True,
            is_private=False
        ).exclude(id=club.id)

        # Ищем по категории
        category_match = similar_clubs.filter(category=club.category)

        # Ищем по тегам
        tag_matches = []
        if club.tags:
            tags = [tag.strip().lower() for tag in club.tags.split(',')]
            for tag in tags:
                tag_match = similar_clubs.filter(tags__icontains=tag)
                tag_matches.extend(tag_match)

        # Ищем по ключевым словам в описании
        text_matches = []
        keywords = self._extract_keywords(club.description)
        for keyword in keywords[:5]:  # Берем первые 5 ключевых слов
            text_match = similar_clubs.filter(
                Q(description__icontains=keyword) |
                Q(tags__icontains=keyword) |
                Q(target_audience__icontains=keyword)
            )
            text_matches.extend(text_match)

        # Объединяем результаты и убираем дубликаты
        all_matches = list(set(
            list(category_match) + tag_matches + text_matches
        ))

        # Сортируем по популярности
        all_matches.sort(key=lambda x: x.members_count + x.likes_count, reverse=True)

        return all_matches[:limit]

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Извлекает ключевые слова из текста
        """
        # Удаляем знаки препинания и приводим к нижнему регистру
        text = re.sub(r'[^\w\s]', ' ', text.lower())

        # Разбиваем на слова и убираем короткие
        words = [word for word in text.split() if len(word) > 3]

        # Возвращаем уникальные слова
        return list(set(words))

    def get_featured_clubs(self, limit: int = 5) -> List[Club]:
        """
        Возвращает рекомендуемые клубы
        """
        return Club.objects.filter(
            is_active=True,
            is_private=False,
            is_featured=True
        ).order_by('-recommendation_score', '-members_count')[:limit]

    def get_popular_clubs(self, limit: int = 5) -> List[Club]:
        """
        Возвращает популярные клубы
        """
        return Club.objects.filter(
            is_active=True,
            is_private=False
        ).order_by('-members_count', '-likes_count')[:limit]

    def get_clubs_by_category(self, category_name: str, limit: int = 10) -> List[Club]:
        """
        Возвращает клубы по категории
        """
        try:
            category = ClubCategory.objects.get(name__iexact=category_name, is_active=True)
            return Club.objects.filter(
                is_active=True,
                is_private=False,
                category=category
            ).order_by('-members_count', '-recommendation_score')[:limit]
        except ClubCategory.DoesNotExist:
            return []
