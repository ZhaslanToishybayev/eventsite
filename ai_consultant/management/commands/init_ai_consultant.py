from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ai_consultant.services_v2 import AIConsultantServiceV2
from ai_consultant.services.context import ContextService
from clubs.models import Club, ClubCategory, City, Festival
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Инициализирует ИИ-консультант с базовыми данными и контекстом'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительно пересоздать все контекстные данные',
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Начинаем инициализацию ИИ-консультанта...')

        ai_service = AIConsultantServiceV2()
        context_service = ContextService()

        try:
            # 1. Инициализация системного контекста
            self.stdout.write('📝 Создаем системный контекст...')
            context_service.initialize_system_contexts()

            # 2. Создание контекста на основе данных платформы
            self.stdout.write('🏗️ Создаем контекст на основе данных платформы...')
            self.create_platform_context(options.get('force', False))

            # 3. Валидация настройки
            self.validate_setup()

            self.stdout.write(
                self.style.SUCCESS('✅ ИИ-консультант успешно инициализирован!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка при инициализации: {str(e)}')
            )
            logger.error(f"AI consultant initialization failed: {str(e)}")

    def create_platform_context(self, force=False):
        """Создает контекст на основе реальных данных платформы"""

        # Контекст о категориях клубов
        categories_context = {
            'key': 'club_categories_info',
            'category': 'clubs',
            'content': self.get_categories_context()
        }

        # Контекст о городах
        cities_context = {
            'key': 'cities_info',
            'category': 'locations',
            'content': self.get_cities_context()
        }

        # Контекст о клубах
        clubs_context = {
            'key': 'active_clubs_info',
            'category': 'clubs',
            'content': self.get_clubs_context()
        }

        # Контекст о фестивалях
        festivals_context = {
            'key': 'festivals_info',
            'category': 'events',
            'content': self.get_festivals_context()
        }

        # Контекст о правилах платформы
        rules_context = {
            'key': 'platform_rules',
            'category': 'rules',
            'content': self.get_platform_rules_context()
        }

        contexts = [
            categories_context,
            cities_context,
            clubs_context,
            festivals_context,
            rules_context
        ]

        from ai_consultant.models import AIContext

        for ctx_data in contexts:
            if force:
                AIContext.objects.filter(key=ctx_data['key']).delete()

            AIContext.objects.get_or_create(
                key=ctx_data['key'],
                defaults=ctx_data
            )

        self.stdout.write(f'   ✅ Создано {len(contexts)} контекстных записей')

    def get_categories_context(self):
        """Формирует контекст о категориях клубов"""
        categories = ClubCategory.objects.filter(is_active=True)
        if not categories.exists():
            return "На платформе доступны различные категории клубов для всех интересов."

        category_list = []
        for cat in categories:
            category_list.append(f"- {cat.name}")

        return f"""Доступные категории клубов на UnitySphere:
{chr(10).join(category_list)}

Каждая категория объединяет клубы со схожими интересами и целями."""

    def get_cities_context(self):
        """Формирует контекст о городах"""
        cities = City.objects.all()[:20]  # Ограничиваем для размера контекста
        if not cities.exists():
            return "Платформа работает в городах Казахстана."

        city_list = []
        for city in cities:
            city_list.append(f"- {city.name}")

        return f"""Платформа UnitySphere активна в следующих городах:
{chr(10).join(city_list[:10])}{"..." if len(city_list) > 10 else ""}

Пользователи могут создавать клубы и находить единомышленников в своем городе."""

    def get_clubs_context(self):
        """Формирует контекст о активных клубах"""
        active_clubs = Club.objects.filter(is_active=True).order_by('-members_count')[:10]
        if not active_clubs.exists():
            return "На платформе активно развиваются сообщества по разным интересам."

        clubs_info = []
        for club in active_clubs:
            clubs_info.append(
                f"- {club.name} ({club.category.name if club.category else 'Без категории'}) - "
                f"{club.members_count} участников"
            )

        return f"""Популярные клубы на UnitySphere:
{chr(10).join(clubs_info)}

Всего на платформе зарегистрировано более {Club.objects.filter(is_active=True).count()} активных клубов."""

    def get_festivals_context(self):
        """Формирует контекст о фестивалях"""
        festivals = Festival.objects.all()
        if not festivals.exists():
            return "Платформа организует фестивали для объединения клубов."

        festivals_info = []
        for festival in festivals.order_by('-created_at')[:5]:
            festivals_info.append(
                f"- {festival.name} ({festival.location or 'Локация уточняется'})"
            )

        return f"""Предстоящие и прошедшие фестивали:
{chr(10).join(festivals_info)}

Фестивали - это отличный способ познакомиться с разными клубами и найти единомышленников."""

    def get_platform_rules_context(self):
        """Формирует контекст о правилах платформы"""
        return """Правила платформы UnitySphere:

🎯 Цели платформы:
- Объединение людей по интересам
- Создание и развитие фан-клубов
- Организация мероприятий и фестивалей
- Партнерство между сообществами

📋 Основные правила:
- Уважительное общение между участниками
- Запрет на спам и рекламу без разрешения
- Соблюдение законодательства РК
- Создание контента, соответствующего тематике клуба

🔒 Приватные клубы:
- Требуют одобрения заявки на вступление
- Управляющие могут устанавливать свои правила
- Возможность создать закрытое сообщество

🤝 Партнерство:
- Клубы могут заключать партнерства
- Совместные мероприятия и проекты
- Обмен опытом и ресурсами

⚠️ Безопасность:
- Администрация платформы следит за порядком
- Возможность пожаловаться на нарушение
- Защита персональных данных пользователей"""

    def validate_setup(self):
        """Проверяет корректность настройки"""
        from django.conf import settings

        # Проверяем наличие API ключа
        if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY не настроен в settings")

        # Проверяем количество контекстных записей
        from ai_consultant.models import AIContext
        context_count = AIContext.objects.filter(is_active=True).count()
        self.stdout.write(f"   📊 Создано контекстных записей: {context_count}")

        # Проверяем наличие активных клубов
        clubs_count = Club.objects.filter(is_active=True).count()
        self.stdout.write(f"   🏠 Активных клубов на платформе: {clubs_count}")

        # Проверяем количество пользователей
        users_count = User.objects.filter(is_active=True).count()
        self.stdout.write(f"   👥 Активных пользователей: {users_count}")