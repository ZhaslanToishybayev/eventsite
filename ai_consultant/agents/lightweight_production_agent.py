#!/usr/bin/env python3
"""
🤖 Lightweight Production AI Agent for UnitySphere
Working без dependency проблем
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any


class LightweightAIConsultant:
    """🤖 Упрощенный AI консультант для production"""

    def __init__(self):
        self.conversation_state = "greeting"
        self.collected_data = {}

    def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """🤖 Обрабатываем сообщение пользователя"""

        message = message.lower().strip()

        # Приветствие
        if self.conversation_state == "greeting":
            return self._handle_greeting(message)

        # Выбор типа клуба
        elif self.conversation_state == "club_type":
            return self._handle_club_type(message)

        # Придумываем название
        elif self.conversation_state == "name_creation":
            return self._handle_name_creation(message)

        # Описание клуба
        elif self.conversation_state == "description":
            return self._handle_description(message)

        # Контактная информация
        elif self.conversation_state == "contacts":
            return self._handle_contacts(message)

        # Финальная проверка
        elif self.conversation_state == "review":
            return self._handle_review(message)

        # Подтверждение создания
        elif self.conversation_state == "confirmation":
            return self._handle_confirmation(message)

        else:
            return self._get_default_response()

    def _handle_greeting(self, message: str) -> Dict[str, Any]:
        """👋 Обработка приветствия"""
        if any(word in message for word in ["привет", "здравствуй", "добрый", "hello", "hi"]):
            response = """👋 Привет! Я - AI консультант UnitySphere.

Готов помочь создать ваш клуб через естественный диалог!

📊 На нашем сайте already есть 420+ активных клубов:
• Технологии: 156 клубов
• Творчество: 98 клубов
• Спорт: 87 клубов
• Бизнес: 65 клубов
• Языки: 45 клубов
• Другие: 29 клубов

💡 Расскажите, какой клуб вы хотите создать?"""
            self.conversation_state = "club_type"
        else:
            response = """👋 Здравствуйте! Я - AI консультант UnitySphere.

Помогу создать ваш клуб через естественный диалог на русском языке.

💡 Например, вы можете сказать:
• "Хочу создать клуб программирования"
• "Нужен фотографический клуб"
• "Ищу спортивный клуб"

Какой клуб вы хотите создать?"""
            self.conversation_state = "club_type"

        return {
            "response": response,
            "state": self.conversation_state,
            "quick_replies": [
                "Клуб программирования",
                "Фотографический клуб",
                "Спортивный клуб",
                "Языковой клуб",
                "Творческий клуб"
            ]
        }

    def _handle_club_type(self, message: str) -> Dict[str, Any]:
        """🏷️ Определяем тип клуба"""
        club_type = self._classify_club_type(message)

        if club_type:
            self.collected_data["club_type"] = club_type
            response = f"""{club_type['category']} ({club_type['count']} клубов)
Примеры: {', '.join(club_type['examples'])}

🎯 Какое конкретное направление вас интересует?"""
            self.conversation_state = "name_creation"
        else:
            response = """🤔 Не совсем понял, какой тип клуба вы хотите создать.

Вот популярные направления:
• Программирование и технологии
• Фотография и дизайн
• Спорт и фитнес
• Изучение языков
• Музыка и творчество
• Бизнес и карьера

Уточните, пожалуйста?"""
            return {
                "response": response,
                "state": self.conversation_state,
                "quick_replies": [
                    "Программирование",
                    "Фотография",
                    "Спорт",
                    "Языки",
                    "Творчество"
                ]
            }

        return {
            "response": response,
            "state": self.conversation_state,
            "data": {"club_type": club_type}
        }

    def _classify_club_type(self, message: str) -> Optional[Dict[str, Any]]:
        """🔍 Классифицируем тип клуба"""

        tech_keywords = ["программ", "код", "dev", "tech", "технолог", "айти", "it", "computer", "coding"]
        photo_keywords = ["фото", "camera", "photo", "дизайн", "design", "график", "art", "искусство"]
        sport_keywords = ["спорт", "фитнес", "gym", "бег", "yoga", "йога", "трениров", "workout"]
        language_keywords = ["язык", "english", "английский", "language", "немецкий", "французский"]
        creative_keywords = ["творчество", "music", "музыка", "рисование", "paint", "handmade", "рукоделие"]
        business_keywords = ["бизнес", "карьера", "работа", "money", "финансы", "start"]

        club_types = {
            "technology": {
                "category": "💻 Технологии и программирование",
                "count": 156,
                "examples": ["Python", "Web-разработка", "Data Science", "Mobile Development"]
            },
            "creative": {
                "category": "🎨 Творчество и искусство",
                "count": 98,
                "examples": ["Фотография", "Графический дизайн", "Музыка", "Рисование"]
            },
            "sport": {
                "category": "🏃‍♂️ Спорт и здоровье",
                "count": 87,
                "examples": ["Йога", "Бег", "Фитнес", "Танцы"]
            },
            "language": {
                "category": "🌐 Языки и общение",
                "count": 45,
                "examples": ["Английский", "Немецкий", "Французский", "Испанский"]
            },
            "business": {
                "category": "💼 Бизнес and карьера",
                "count": 65,
                "examples": ["Стартапы", "Маркетинг", "Лидерство", "Инвестиции"]
            }
        }

        if any(word in message for word in tech_keywords):
            return club_types["technology"]
        elif any(word in message for word in photo_keywords):
            return club_types["creative"]
        elif any(word in message for word in sport_keywords):
            return club_types["sport"]
        elif any(word in message for word in language_keywords):
            return club_types["language"]
        elif any(word in message for word in business_keywords):
            return club_types["business"]
        else:
            return None

    def _handle_name_creation(self, message: str) -> Dict[str, Any]:
        """📝 Придумываем название"""
        club_type = self.collected_data.get("club_type", {}).get("category", "клуб")

        suggestions = self._generate_name_suggestions(club_type)

        response = f"""📝 Давайте придумаем крутые названия для вашего {club_type.lower()}!

Вот несколько вариантов:
{chr(10).join([f"• <b>{name}</b>" for name in suggestions[:5]])}

Какое название нравится? Или предложите свое!"""

        self.conversation_state = "description"

        return {
            "response": response,
            "state": self.conversation_state,
            "quick_replies": suggestions[:3]
        }

    def _generate_name_suggestions(self, club_type: str) -> List[str]:
        """✨ Генерируем названия"""
        if "технолог" in club_type.lower():
            return [
                "Tech Masters Almaty",
                "Future Developers",
                "Code Crafters Club",
                "IT Hub Kazakhstan",
                "Programming Pioneers"
            ]
        elif "творчество" in club_type.lower():
            return [
                "Creative Minds Studio",
                "Art & Soul Collective",
                "Design Mavericks",
                "Infinite Canvas Club",
                "Visionary Artists"
            ]
        elif "спорт" in club_type.lower():
            return [
                "Active Life Community",
                "Fitness Family Almaty",
                "Sports Enthusiasts Hub",
                "Healthy Lifestyle Club",
                "Energy & Movement"
            ]
        elif "язык" in club_type.lower():
            return [
                "Language Exchange Club",
                "Polyglot Community",
                "Speak & Learn",
                "World Languages Hub",
                "Conversation Club"
            ]
        else:
            return [
                "Amazing Club",
                "Community of Enthusiasts",
                "Passion Project",
                "Dream Team",
                "Success Makers"
            ]

    def _handle_description(self, message: str) -> Dict[str, Any]:
        """✍️ Создаем описание"""
        club_type = self.collected_data.get("club_type", {}).get("category", "клуб")

        template = self._get_description_template(club_type)

        response = f"""✍️ Создадим профессиональное описание для вашего {club_type.lower()}.

{template}

🔥 <b>Популярные темы в вашей категории:</b>
{self._get_popular_topics(club_type)}

Хотите использовать это описание или внести изменения?"""

        self.conversation_state = "contacts"

        return {
            "response": response,
            "state": self.conversation_state,
            "quick_replies": [
                "Использовать как есть",
                "Внести изменения",
                "Показать другой вариант"
            ]
        }

    def _get_description_template(self, club_type: str) -> str:
        """📝 Шаблон описания"""
        if "технолог" in club_type.lower():
            return """<b>Наш клуб объединяет людей, увлеченных современными технологиями и программированием.</b>

Мы проводим регулярные встречи, мастер-классы и хакатоны для обмена опытом и развития навыков. В клубе царит дружеская атмосфера, где каждый может найти единомышленников и научиться чем-то новому.

Присоединяйтесь к нашему сообществу разработчиков!"""
        elif "творчество" in club_type.lower():
            return """<b>Наш клуб объединяет творческих людей, увлеченных искусством и самовыражением.</b>

Мы проводим творческие встречи, мастер-классы и выставки для вдохновения и развития навыков. В клубе царит атмосфера свободы и вдохновения, где каждый может раскрыть свой потенциал.

Присоединяйтесь к нашему творческому сообществу!"""
        elif "спорт" in club_type.lower():
            return """<b>Наш клуб объединяет людей, стремящихся к здоровому образу жизни и физической активности.</b>

Мы проводим тренировки, соревнования и мероприятия для поддержания формы и мотивации. В клубе царит атмосфера дружбы и поддержки, где каждый может достичь своих целей.

Присоединяйтесь к нашему спортивному сообществу!"""
        else:
            return """<b>Наш клуб объединяет людей, увлеченных [тема].</b>

Мы проводим регулярные встречи, мастер-классы и мероприятия для обмена опытом и развития навыков. В клубе царит дружеская атмосфера, где каждый может найти единомышленников и научиться чему-то новому.

Присоединяйтесь к нашему сообществу!"""

    def _get_popular_topics(self, club_type: str) -> str:
        """🔥 Популярные темы"""
        if "технолог" in club_type.lower():
            return "Python, Веб-разработка, Data Analysis, Machine Learning, Mobile Development"
        elif "творчество" in club_type.lower():
            return "Фотография, Графический дизайн, Иллюстрация, Рукоделие, Музыка"
        elif "спорт" in club_type.lower():
            return "Йога, Бег, Фитнес, Танцы, Силовые тренировки"
        elif "язык" in club_type.lower():
            return "Разговорная практика, Грамматика, Путешествия, Культура, Бизнес-язык"
        else:
            return "Активности по интересам, Встречи, Мастер-классы, События"

    def _handle_contacts(self, message: str) -> Dict[str, Any]:
        """📞 Собираем контактную информацию"""
        response = """📞 Теперь соберем контактную информацию для успешного создания клуба:

<b>Обязательно:</b>
• Email для связи (будет виден участникам)
• Город проведения встреч

<b>По желанию:</b>
• Телефон для связи
• Формат встреч: очные/онлайн/гибрид
• Социальные сети
• Дополнительные контакты

Пожалуйста, укажите доступную информацию."""

        self.conversation_state = "review"

        return {
            "response": response,
            "state": self.conversation_state
        }

    def _handle_review(self, message: str) -> Dict[str, Any]:
        """👀 Финальная проверка"""
        # Здесь можно сохранить собранную информацию
        self.collected_data["user_message"] = message

        response = f"""👀 Давайте проверим все детали перед публикацией:

• <b>Тип клуба:</b> {self.collected_data.get('club_type', {}).get('category', 'Не указано')}
• <b>Описание:</b> {message[:100]}...
• <b>Контакты:</b> {message}

<b>Все верно?</b> Напишите "готово" для подтверждения или укажите изменения."""

        self.conversation_state = "confirmation"

        return {
            "response": response,
            "state": self.conversation_state,
            "quick_replies": [
                "Готово",
                "Внести изменения",
                "Начать заново"
            ]
        }

    def _handle_confirmation(self, message: str) -> Dict[str, Any]:
        """✅ Подтверждение создания"""
        if "готов" in message.lower() or "да" in message.lower():
            response = """✅ Отлично! Ваш клуб успешно создан! 🎉

Модераторы скоро проверят и опубликуют его на сайте. Вы получите уведомление, когда клуб будет доступен.

Спасибо за создание нового сообщества! 🚀

<b>Что дальше?</b>
• Поделитесь клубом с друзьями
• Пригласите единомышленников
• Организуйте первую встречу
• Регулярно обновляйте информацию

Хотите создать еще один клуб?"""
            self.conversation_state = "greeting"
            self.collected_data = {}
        else:
            response = "Понял, внесем изменения. Что нужно изменить?"
            self.conversation_state = "review"

        return {
            "response": response,
            "state": self.conversation_state,
            "action": "club_created" if "готов" in message.lower() else "continue_editing"
        }

    def _get_default_response(self) -> Dict[str, Any]:
        """❓ Стандартный ответ"""
        return {
            "response": "Я не совсем понял ваш ответ. Пожалуйста, уточните или выберите из предложенных вариантов.",
            "state": self.conversation_state,
            "quick_replies": [
                "Повторить",
                "Начать заново",
                "Помощь"
            ]
        }


# Глобальный экземпляр агента
ai_consultant = LightweightAIConsultant()


def get_ai_response(message: str, session_id: str = "default") -> Dict[str, Any]:
    """🎯 Получаем AI ответ"""
    return ai_consultant.process_message(message, session_id)