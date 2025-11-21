"""
Enhanced Club Creation Validator
Provides comprehensive validation for club creation with detailed error messages.
"""
import re
from typing import Dict, List, Tuple
from django.contrib.auth import get_user_model

User = get_user_model()


class ClubCreationValidator:
    """
    Валидатор для создания клубов с детальными проверками
    """
    
    # Validation rules
    MIN_NAME_LENGTH = 3
    MAX_NAME_LENGTH = 100
    MIN_DESCRIPTION_LENGTH = 200
    MAX_DESCRIPTION_LENGTH = 5000
    
    # Forbidden words in club names
    FORBIDDEN_WORDS = [
        'admin', 'administrator', 'moderator', 'official', 
        'test', 'тест', 'spam', 'спам'
    ]
    
    # Required categories
    VALID_CATEGORIES = [
        'Спорт', 'Хобби', 'Профессия', 'IT', 'Творчество', 
        'Образование', 'Бизнес', 'Социальные'
    ]
    
    @classmethod
    def validate_club_name(cls, name: str) -> Tuple[bool, str]:
        """
        Валидация названия клуба
        Returns: (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "❌ Название клуба не может быть пустым"
        
        name = name.strip()
        
        # Length check
        if len(name) < cls.MIN_NAME_LENGTH:
            return False, f"❌ Название слишком короткое (минимум {cls.MIN_NAME_LENGTH} символа)"
        
        if len(name) > cls.MAX_NAME_LENGTH:
            return False, f"❌ Название слишком длинное (максимум {cls.MAX_NAME_LENGTH} символов)"
        
        # Forbidden words check
        name_lower = name.lower()
        for forbidden in cls.FORBIDDEN_WORDS:
            if forbidden in name_lower:
                return False, f"❌ Название содержит запрещенное слово: '{forbidden}'"
        
        # Check for only special characters
        if not re.search(r'[a-zA-Zа-яА-ЯёЁ]', name):
            return False, "❌ Название должно содержать хотя бы одну букву"
        
        # Check for excessive special characters
        special_chars = len(re.findall(r'[^a-zA-Zа-яА-ЯёЁ0-9\s]', name))
        if special_chars > len(name) // 2:
            return False, "❌ Слишком много специальных символов в названии"
        
        return True, ""
    
    @classmethod
    def validate_description(cls, description: str) -> Tuple[bool, str]:
        """
        Валидация описания клуба
        Returns: (is_valid, error_message)
        """
        if not description or not description.strip():
            return False, "❌ Описание клуба не может быть пустым"
        
        description = description.strip()
        
        # Length check
        if len(description) < cls.MIN_DESCRIPTION_LENGTH:
            return False, f"❌ Описание слишком короткое (минимум {cls.MIN_DESCRIPTION_LENGTH} символов, сейчас {len(description)})"
        
        if len(description) > cls.MAX_DESCRIPTION_LENGTH:
            return False, f"❌ Описание слишком длинное (максимум {cls.MAX_DESCRIPTION_LENGTH} символов)"
        
        # Check for meaningful content (not just repeated characters)
        unique_chars = len(set(description.replace(' ', '').replace('\n', '')))
        if unique_chars < 10:
            return False, "❌ Описание должно содержать более разнообразный текст"
        
        # Check for at least some sentences
        sentences = len(re.findall(r'[.!?]+', description))
        if sentences < 2:
            return False, "❌ Описание должно содержать хотя бы 2-3 предложения"
        
        return True, ""
    
    @classmethod
    def validate_category(cls, category_name: str) -> Tuple[bool, str]:
        """
        Валидация категории
        Returns: (is_valid, error_message)
        """
        if not category_name or not category_name.strip():
            return False, "❌ Категория не указана"
        
        # Fuzzy match with valid categories
        category_lower = category_name.lower()
        for valid_cat in cls.VALID_CATEGORIES:
            if valid_cat.lower() in category_lower or category_lower in valid_cat.lower():
                return True, ""
        
        return False, f"❌ Неизвестная категория. Доступные: {', '.join(cls.VALID_CATEGORIES)}"
    
    @classmethod
    def validate_user_permissions(cls, user) -> Tuple[bool, str]:
        """
        Проверка прав пользователя на создание клуба
        Returns: (is_valid, error_message)
        """
        if not user or not user.is_authenticated:
            return False, "❌ Необходимо авторизоваться для создания клуба"
        
        # Check if user has email
        if not user.email:
            return False, "❌ У пользователя должен быть указан email"
        
        # Check if user is not banned (if such field exists)
        if hasattr(user, 'is_banned') and user.is_banned:
            return False, "❌ Пользователь заблокирован и не может создавать клубы"
        
        return True, ""
    
    @classmethod
    def validate_all(cls, user, name: str, description: str, category: str) -> Tuple[bool, List[str]]:
        """
        Полная валидация всех полей
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate user
        is_valid, error = cls.validate_user_permissions(user)
        if not is_valid:
            errors.append(error)
        
        # Validate name
        is_valid, error = cls.validate_club_name(name)
        if not is_valid:
            errors.append(error)
        
        # Validate description
        is_valid, error = cls.validate_description(description)
        if not is_valid:
            errors.append(error)
        
        # Validate category
        is_valid, error = cls.validate_category(category)
        if not is_valid:
            errors.append(error)
        
        return len(errors) == 0, errors
    
    @classmethod
    def suggest_improvements(cls, name: str, description: str) -> List[str]:
        """
        Предлагает улучшения для названия и описания
        Returns: list of suggestions
        """
        suggestions = []
        
        # Name suggestions
        if name and len(name) < 10:
            suggestions.append("💡 Рекомендация: Добавьте город или специализацию в название (например, 'Шахматный клуб Алматы')")
        
        # Description suggestions
        if description:
            if len(description) < 300:
                suggestions.append("💡 Рекомендация: Расширьте описание - расскажите о целях, мероприятиях и преимуществах клуба")
            
            if 'встреч' not in description.lower() and 'событи' not in description.lower():
                suggestions.append("💡 Рекомендация: Укажите, какие мероприятия или встречи планируются")
            
            if not any(word in description.lower() for word in ['присоединяйтесь', 'добро пожаловать', 'ждем']):
                suggestions.append("💡 Рекомендация: Добавьте призыв к действию в конце описания")
        
        return suggestions


class ClubCreationConfirmation:
    """
    Генерирует сообщения подтверждения перед созданием клуба
    """
    
    @staticmethod
    def generate_confirmation_message(name: str, description: str, category: str, city: str = None, is_private: bool = False) -> str:
        """
        Генерирует сообщение подтверждения с предпросмотром клуба
        """
        message = "🎯 **Подтверждение создания клуба**\n\n"
        message += "Пожалуйста, проверьте данные перед созданием:\n\n"
        
        message += f"📌 **Название:** {name}\n"
        message += f"📂 **Категория:** {category}\n"
        
        if city:
            message += f"🌍 **Город:** {city}\n"
        
        message += f"🔒 **Тип:** {'Приватный' if is_private else 'Публичный'}\n\n"
        
        message += f"📝 **Описание:**\n{description[:200]}{'...' if len(description) > 200 else ''}\n\n"
        
        message += "✅ **Что произойдет после создания:**\n"
        message += "• Клуб будет создан и опубликован на платформе\n"
        message += "• Вы станете создателем и администратором\n"
        message += "• Вы сможете приглашать участников\n"
        message += "• Вы сможете создавать события и публикации\n\n"
        
        message += "⚠️ **Важно:** После создания название клуба нельзя будет изменить\n\n"
        message += "Подтвердите создание клуба, ответив 'Да' или 'Подтверждаю'"
        
        return message
    
    @staticmethod
    def generate_success_message(club_name: str, club_id: str, link: str) -> str:
        """
        Генерирует сообщение об успешном создании клуба
        """
        message = "🎉 **Поздравляем! Клуб успешно создан!** 🎉\n\n"
        message += f"✅ **Название:** {club_name}\n"
        message += f"🔗 **Ссылка:** {link}\n\n"
        
        message += "📋 **Следующие шаги:**\n"
        message += "1. 📸 Загрузите логотип клуба\n"
        message += "2. 📅 Создайте первое событие\n"
        message += "3. 👥 Пригласите первых участников\n"
        message += "4. 📝 Опубликуйте приветственный пост\n"
        message += "5. ⚙️ Настройте права доступа для модераторов\n\n"
        
        message += "💡 **Советы для успешного старта:**\n"
        message += "• Пригласите 5-10 друзей для начала\n"
        message += "• Запланируйте первую встречу на ближайшие 2 недели\n"
        message += "• Создайте контент-план на первый месяц\n"
        message += "• Регулярно публикуйте новости и обновления\n\n"
        
        message += "Удачи в развитии вашего сообщества! 🚀"
        
        return message
