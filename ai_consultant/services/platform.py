import json
from typing import List, Dict, Optional
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from ..models import PlatformService

User = get_user_model()


class PlatformServiceManager:
    """
    Сервис для управления услугами платформы
    """

    def __init__(self):
        self.default_services = self._get_default_services()

    def _get_default_services(self) -> List[Dict]:
        """Возвращает список услуг по умолчанию"""
        return [
            # Аренда оборудования
            {
                'title': 'Аренда фотостудии',
                'service_type': 'rental',
                'description': 'Профессиональная фотостудия со студийным светом, фонами и оборудованием для фотосессий и видео съемок. Площадь 50м², высокие потолки 3.5м.',
                'price_info': '3 000 тг/час, минимальная аренда 2 часа',
                'contact_info': 'studio@fan-club.kz | +7 775 123 45 67',
                'order': 1
            },
            {
                'title': 'Аренда проектора и экрана',
                'service_type': 'rental',
                'description': 'Современный проектор с яркостью 5000 люмен и экран 200х150см для презентаций, семинаров и мероприятий. Включает установку и настройку.',
                'price_info': '5 000 тг/день',
                'contact_info': 'equipment@fan-club.kz | +7 775 123 45 68',
                'order': 2
            },
            {
                'title': 'Аренда звукового оборудования',
                'service_type': 'rental',
                'description': 'Комплект аудиооборудования для мероприятий: микрофоны, колонки, микшерный пульт. Подходит для конференций до 100 человек.',
                'price_info': '10 000 тг/день',
                'contact_info': 'sound@fan-club.kz | +7 775 123 45 69',
                'order': 3
            },

            # Печать и вышивка
            {
                'title': 'Печать футболок и худи',
                'service_type': 'printing',
                'description': 'Качественная печать на текстиле методом ДТГ. Возможна печать ваших дизайнов или выбор из каталога. Минимальный заказ 5 штук.',
                'price_info': 'от 4 500 тг/шт (зависит от размера и сложности)',
                'contact_info': 'print@fan-club.kz | +7 775 123 45 70',
                'order': 4
            },
            {
                'title': 'Вышивка логотипов на одежде',
                'service_type': 'printing',
                'description': 'Профессиональная машинная вышивка логотипов и надписей на футболках, кепках, толстовках. Долговечное и качественное оформление.',
                'price_info': 'от 2 000 тг/логотип',
                'contact_info': 'embroidery@fan-club.kz | +7 775 123 45 71',
                'order': 5
            },
            {
                'title': 'Изготовление сувенирной продукции',
                'service_type': 'printing',
                'description': 'Производство брендированной сувенирной продукции: кружки, ручки, блокноты, брелоки, магниты с вашим логотипом.',
                'price_info': 'от 500 тг/шт',
                'contact_info': 'merch@fan-club.kz | +7 775 123 45 72',
                'order': 6
            },

            # Консультации специалистов
            {
                'title': 'Маркетинговая консультация',
                'service_type': 'consultation',
                'description': 'Индивидуальная консультация по маркетингу для вашего клуба или проекта. Анализ целевой аудитории, стратегии продвижения, SMM.',
                'price_info': '8 000 тг/час (первая консультация 30 минут бесплатно)',
                'contact_info': 'marketing@fan-club.kz | +7 775 123 45 73',
                'order': 7
            },
            {
                'title': 'Юридическая консультация',
                'service_type': 'consultation',
                'description': 'Консультация по юридическим вопросам: регистрация клуба, договоры, налоги, авторские права. Специализация на некоммерческих организациях.',
                'price_info': '10 000 тг/час',
                'contact_info': 'legal@fan-club.kz | +7 775 123 45 74',
                'order': 8
            },
            {
                'title': 'IT-консультация',
                'service_type': 'consultation',
                'description': 'Помощь в выборе технических решений для клуба: сайт, приложения, автоматизация, SEO-оптимизация, аналитика.',
                'price_info': '12 000 тг/час',
                'contact_info': 'it@fan-club.kz | +7 775 123 45 75',
                'order': 9
            },
            {
                'title': 'Консультация по организационному развитию',
                'service_type': 'consultation',
                'description': 'Помощь в развитии клуба: привлечение участников, организация мероприятий, фандрейтинг, волонтерская программа.',
                'price_info': '7 000 тг/час',
                'contact_info': 'development@fan-club.kz | +7 775 123 45 76',
                'order': 10
            },

            # Студия интервью
            {
                'title': 'Запись подкаста',
                'service_type': 'studio',
                'description': 'Полностью оборудованная студия для записи подкастов. Профессиональные микрофоны, звукоизоляция, помощь монтажера.',
                'price_info': '6 000 тг/час (включает помощь оператора)',
                'contact_info': 'studio@fan-club.kz | +7 775 123 45 77',
                'order': 11
            },
            {
                'title': 'Видеозапись интервью',
                'service_type': 'studio',
                'description': 'Профессиональная видеозапись интервью, выступлений, вебинаров. 2 камеры, студийный свет, звук.',
                'price_info': '15 000 тг/час',
                'contact_info': 'video@fan-club.kz | +7 775 123 45 78',
                'order': 12
            },
            {
                'title': 'Онлайн-трансляция мероприятий',
                'service_type': 'studio',
                'description': 'Организация профессиональной онлайн-трансляции вашего мероприятия на платформы YouTube, Instagram, Zoom.',
                'price_info': '20 000 тг/мероприятие',
                'contact_info': 'streaming@fan-club.kz | +7 775 123 45 79',
                'order': 13
            }
        ]

    def initialize_services(self):
        """Инициализирует услуги в базе данных"""
        for service_data in self.default_services:
            service, created = PlatformService.objects.get_or_create(
                title=service_data['title'],
                defaults=service_data
            )
            if created:
                print(f"✅ Создана услуга: {service.title}")

    def get_services_by_type(self, service_type: str) -> List[PlatformService]:
        """Возвращает услуги определенного типа"""
        return PlatformService.objects.filter(
            service_type=service_type,
            is_active=True
        ).order_by('order', 'title')

    def get_all_services(self) -> List[PlatformService]:
        """Возвращает все активные услуги"""
        return PlatformService.objects.filter(
            is_active=True
        ).order_by('order', 'title')

    def get_featured_services(self, limit: int = 6) -> List[PlatformService]:
        """Возвращает рекомендуемые услуги"""
        return PlatformService.objects.filter(
            is_active=True
        ).order_by('order', 'title')[:limit]

    def get_service_recommendations(self, user_context: Dict) -> List[PlatformService]:
        """
        Возвращает персонализированные рекомендации услуг на основе контекста пользователя
        """
        recommendations = []
        all_services = self.get_all_services()

        # Анализируем контекст пользователя
        interests = user_context.get('interests', '').lower()
        goals = user_context.get('goals', '').lower()
        has_club = user_context.get('has_club', False)

        # Правила рекомендации
        if any(word in interests for word in ['фото', 'видео', 'съемка', 'контент']):
            photo_services = [s for s in all_services if 'фотостудия' in s.title.lower() or 'видео' in s.title.lower()]
            recommendations.extend(photo_services)

        if any(word in interests for word in ['бизнес', 'маркетинг', 'продвижение']):
            marketing_services = [s for s in all_services if 'маркетинг' in s.title.lower()]
            recommendations.extend(marketing_services)

        if has_club or any(word in goals for word in ['клуб', 'сообщество', 'организация']):
            club_services = [s for s in all_services if any(
                keyword in s.description.lower()
                for keyword in ['клуб', 'мероприятие', 'участник', 'организация']
            )]
            recommendations.extend(club_services)

        if any(word in interests for word in ['подкаст', 'интервью', 'медиа']):
            media_services = [s for s in all_services if 'подкаст' in s.title.lower() or 'интервью' in s.title.lower()]
            recommendations.extend(media_services)

        # Если нет конкретных рекомендаций, возвращаем популярные услуги
        if not recommendations:
            recommendations = self.get_featured_services(4)

        # Убираем дубликаты и сохраняем порядок
        seen_ids = set()
        unique_recommendations = []
        for service in recommendations:
            if service.id not in seen_ids:
                unique_recommendations.append(service)
                seen_ids.add(service.id)

        return unique_recommendations[:4]

    def search_services(self, query: str) -> List[PlatformService]:
        """Поиск услуг по ключевым словам"""
        query_lower = query.lower()
        services = self.get_all_services()

        results = []
        for service in services:
            if (query_lower in service.title.lower() or
                query_lower in service.description.lower() or
                query_lower in service.get_service_type_display().lower()):
                results.append(service)

        return results

    def get_service_by_id(self, service_id: str) -> Optional[PlatformService]:
        """Возвращает услугу по ID"""
        try:
            return PlatformService.objects.get(id=service_id, is_active=True)
        except PlatformService.DoesNotExist:
            return None

    def get_similar_services(self, service: PlatformService, limit: int = 3) -> List[PlatformService]:
        """Возвращает похожие услуги"""
        return PlatformService.objects.filter(
            service_type=service.service_type,
            is_active=True
        ).exclude(id=service.id).order_by('order', 'title')[:limit]

    def format_service_for_ai(self, service: PlatformService) -> str:
        """Форматирует услугу для отображения в ответе ИИ"""
        return f"""📋 **{service.title}**
🏷️ Тип: {service.get_service_type_display()}
📝 Описание: {service.description}
💰 Цена: {service.price_info}
📞 Контакты: {service.contact_info}"""

    def create_service_request(self, user: User, service_id: str, request_data: Dict) -> Dict:
        """
        Создает заявку на услугу (заглушка для будущей функциональности)
        """
        service = self.get_service_by_id(service_id)
        if not service:
            return {
                'success': False,
                'error': 'Услуга не найдена'
            }

        # Здесь можно добавить логику создания заявки
        return {
            'success': True,
            'message': f'Ваша заявка на услугу "{service.title}" отправлена!',
            'service_title': service.title,
            'contact_info': service.contact_info,
            'next_steps': [
                f'Свяжитесь с нами: {service.contact_info}',
                'Уточните детали и время',
                'Обсудите стоимость и условия'
            ]
        }

    def get_guidance(self, message: str) -> str:
        """
        Возвращает информацию об услугах платформы
        """
        message_lower = message.lower()

        # Инициализируем услуги, если они еще не созданы
        self.initialize_services()

        if any(word in message_lower for word in ['аренда', 'снять', 'оборудование', 'студия']):
            services = self.get_services_by_type('rental')

            if services:
                response = "🏠 **Аренда оборудования и площадок**\n\n"
                for service in services[:3]:
                    response += f"**{service.title}**\n"
                    response += f"{service.description}\n"
                    response += f"💰 {service.price_info}\n"
                    response += f"📞 {service.contact_info}\n\n"

                response += "**📋 Как арендовать:**\n"
                response += "1. Выберите нужное оборудование/площадку\n"
                response += "2. Свяжитесь с нами для бронирования\n"
                response += "3. Укажите дату и время\n"
                response += "4. Получите подтверждение\n\n"
                response += "Хотите забронировать что-то конкретное?"
            else:
                response = "К сожалению, сейчас нет доступной техники для аренды. Попробуйте позже."

        elif any(word in message_lower for word in ['печать', 'футболка', 'худи', 'вышивка', 'логотип', 'мерч']):
            services = self.get_services_by_type('printing')

            if services:
                response = "👕 **Печать и брендирование**\n\n"
                for service in services[:3]:
                    response += f"**{service.title}**\n"
                    response += f"{service.description}\n"
                    response += f"💰 {service.price_info}\n"
                    response += f"📞 {service.contact_info}\n\n"

                response += "**🎨 Процесс заказа:**\n"
                response += "1. Подготовьте дизайн или выберите из каталога\n"
                response += "2. Отправьте макет на согласование\n"
                response += "3. Утвердите образец\n"
                response += "4. Получите готовую продукцию\n\n"
                response += "Какую продукцию вы хотели бы заказать?"
            else:
                response = "Сейчас услуги печати недоступны. Попробуйте обратиться позже."

        elif any(word in message_lower for word in ['консультация', 'совет', 'специалист', 'эксперт']):
            services = self.get_services_by_type('consultation')

            if services:
                response = "👨‍💼 **Консультации специалистов**\n\n"
                for service in services:
                    response += f"**{service.title}**\n"
                    response += f"{service.description}\n"
                    response += f"💰 {service.price_info}\n"
                    response += f"📞 {service.contact_info}\n\n"

                response += "**📅 Как записаться на консультацию:**\n"
                response += "1. Выберите нужного специалиста\n"
                response += "2. Свяжитесь для записи на удобное время\n"
                response += "3. Опишите вашу ситуацию\n"
                response += "4. Получите профессиональную помощь\n\n"
                response += "Какая консультация вас интересует?"
            else:
                response = "Специалисты сейчас заняты. Попробуйте обратиться в ближайшее время."

        elif any(word in message_lower for word in ['студия', 'подкаст', 'интервью', 'трансляция', 'запись']):
            services = self.get_services_by_type('studio')

            if services:
                response = "🎙️ **Студия и медиа-услуги**\n\n"
                for service in services:
                    response += f"**{service.title}**\n"
                    response += f"{service.description}\n"
                    response += f"💰 {service.price_info}\n"
                    response += f"📞 {service.contact_info}\n\n"

                response += "**🎬 Как забронировать студию:**\n"
                response += "1. Выберите тип услуги (запись/трансляция)\n"
                response += "2. Забронируйте время и дату\n"
                response += "3. Получите техническую поддержку\n"
                response += "4. Проведите запись или трансляцию\n\n"
                response += "Готовы записать подкаст или интервью?"
            else:
                response = "Студия сейчас занята. Выберите другое время, пожалуйста."

        else:
            # Общая информация обо всех услугах
            response = "🎯 **Услуги платформы ЦЕНТР СОБЫТИЙ**\n\n"
            response += "Мы предлагаем полный спектр услуг для развития вашего проекта:\n\n"

            response += "🏠 **Аренда оборудования:**\n"
            response += "• Фотостудия и оборудование\n"
            response += "• Проекторы и экраны\n"
            response += "• Звуковое оборудование\n\n"

            response += "👕 **Печать и брендирование:**\n"
            response += "• Футболки и худи с печатью\n"
            response += "• Вышивка логотипов\n"
            response += "• Сувенирная продукция\n\n"

            response += "👨‍💼 **Консультации специалистов:**\n"
            response += "• Маркетинговые консультации\n"
            response += "• Юридическая поддержка\n"
            response += "• IT-консалтинг\n"
            response += "• Организационное развитие\n\n"

            response += "🎙️ **Студия и медиа:**\n"
            response += "• Запись подкастов\n"
            response += "• Видеозапись интервью\n"
            response += "• Онлайн-трансляции\n\n"

            response += "**📞 Как заказать услугу:**\n"
            response += "1. Расскажите, какая услуга вас интересует\n"
            response += "2. Я предоставлю подробную информацию\n"
            response += "3. Свяжитесь с указанными контактами\n"
            response += "4. Обсудите детали и забронируйте\n\n"

            response += "Какая услуга вас интересует больше всего?"

        return response