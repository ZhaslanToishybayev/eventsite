from typing import Dict

class LanguageService:
    """
    Сервис для работы с языками и локализацией
    """
    
    SUPPORTED_LANGUAGES = ['ru', 'en', 'kk']
    
    SYSTEM_PROMPTS = {
        'ru': "Ты - полезный ИИ-ассистент платформы UnitySphere. Отвечай на русском языке.",
        'en': "You are a helpful AI assistant for UnitySphere platform. Answer in English.",
        'kk': "Сіз UnitySphere платформасының пайдалы AI көмекшісісіз. Қазақ тілінде жауап беріңіз."
    }
    
    def detect_language(self, text: str) -> str:
        """
        Определение языка текста
        """
        if not text:
            return 'ru'
            
        text = text.lower()
        
        # Проверка специфических казахских букв
        if any(char in text for char in 'әіңғүұқөһ'):
            return 'kk'
            
        # Проверка кириллицы (русский)
        cyrillic_chars = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
        has_cyrillic = any(char in text for char in cyrillic_chars)
        
        # Проверка латиницы (английский)
        latin_chars = 'abcdefghijklmnopqrstuvwxyz'
        has_latin = any(char in text for char in latin_chars)
        
        if has_cyrillic:
            return 'ru'
        if has_latin:
            return 'en'
            
        return 'ru'  # По умолчанию
        
    def get_system_prompt(self, language: str) -> str:
        """
        Получение системного промпта для языка
        """
        return self.SYSTEM_PROMPTS.get(language, self.SYSTEM_PROMPTS['ru'])
