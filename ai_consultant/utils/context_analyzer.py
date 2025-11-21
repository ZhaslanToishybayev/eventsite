"""
🧠 Context Analyzer
Утилита для анализа контекста сообщений и диалогов
"""

import re
import logging
from typing import Dict, List, Any, Tuple
from collections import Counter
logger = logging.getLogger(__name__)

try:
    import spacy
    SPACY_AVAILABLE = True
    try:
        nlp = spacy.load("ru_core_news_sm")
    except OSError:
        # Если русская модель не найдена, попробуем английскую
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Если и английская не найдена, отключим spacy
            nlp = None
            SPACY_AVAILABLE = False
            logger.warning("⚠️ spaCy модели не найдены, используется базовый анализ")
except (ImportError, OSError):
    spacy = None
    nlp = None
    SPACY_AVAILABLE = False
    logger.warning("⚠️ spaCy недоступен, используется базовый анализ")


class ContextAnalyzer:
    """
    🔍 Анализатор контекста для извлечения интентов, сущностей и тональности
    """

    def __init__(self):
        # Паттерны для интентов
        self.intent_patterns = {
            'club_creation': [
                r'создать клуб', r'как создать', r'зарегистрировать клуб',
                r'основать клуб', r'открыть клуб', r'новый клуб'
            ],
            'club_joining': [
                r'вступить в клуб', r'присоединиться', r'как вступить',
                r'участие в клубе', r'стать участником'
            ],
            'event_creation': [
                r'создать мероприятие', r'организовать событие',
                r'провести фестиваль', r'новое мероприятие'
            ],
            'technical_help': [
                r'не работает', r'ошибка', r'проблема', r'баг',
                r'помощь', r'поддержка', r'технический вопрос'
            ],
            'information_request': [
                r'что такое', r'расскажи о', r'информация о',
                r'как работает', r'для чего нужен'
            ],
            'recommendation': [
                r'посоветуй', r'рекомендуй', r'какой выбрать',
                r'лучший клуб', r'интересные мероприятия'
            ]
        }

        # Сущности и ключевые слова
        self.entity_patterns = {
            'club_type': [
                r'спортивный клуб', r'музыкальный клуб', r'книжный клуб',
                r'ит клуб', r'танцевальный клуб', r'художественный клуб'
            ],
            'event_type': [
                r'фестиваль', r'конференция', r'семинар', r'воркшоп',
                r'соревнование', r'концерт', r'выставка'
            ],
            'time_period': [
                r'завтра', r'сегодня', r'на следующей неделе', r'в этом месяце',
                r'скоро', r'близко'
            ],
            'location': [
                r'в нашем городе', r'онлайн', r'офлайн', r'в центре',
                r'в университете'
            ]
        }

        # Sentiment словарь (упрощенный)
        self.positive_words = [
            'отлично', 'хорошо', 'здорово', 'супер', 'класс', 'замечательно',
            'спасибо', 'благодарю', 'удобно', 'понравилось'
        ]

        self.negative_words = [
            'плохо', 'ужасно', 'отвратительно', 'проблема', 'ошибка',
            'неудобно', 'сложно', 'непонятно', 'не работает', 'бесполезно'
        ]

    def analyze_message(self, text: str) -> Dict[str, Any]:
        """
        🔍 Полный анализ сообщения
        """
        try:
            analysis = {
                'original_text': text,
                'cleaned_text': self._clean_text(text),
                'intent': None,
                'confidence': 0.0,
                'entities': [],
                'sentiment': 'neutral',
                'sentiment_score': 0.0,
                'urgency': 'normal',
                'keywords': [],
                'language': self._detect_language(text),
                'complexity': self._assess_complexity(text)
            }

            # Определение интента
            intent_result = self._detect_intent(analysis['cleaned_text'])
            analysis['intent'] = intent_result['intent']
            analysis['confidence'] = intent_result['confidence']

            # Извлечение сущностей
            analysis['entities'] = self._extract_entities(analysis['cleaned_text'])

            # Анализ тональности
            sentiment_result = self._analyze_sentiment(analysis['cleaned_text'])
            analysis['sentiment'] = sentiment_result['sentiment']
            analysis['sentiment_score'] = sentiment_result['score']

            # Оценка срочности
            analysis['urgency'] = self._assess_urgency(analysis['cleaned_text'])

            # Извлечение ключевых слов
            analysis['keywords'] = self._extract_keywords(analysis['cleaned_text'])

            return analysis

        except Exception as e:
            logger.error(f"❌ Error analyzing message: {e}")
            return {
                'original_text': text,
                'intent': 'general',
                'confidence': 0.0,
                'entities': [],
                'sentiment': 'neutral',
                'error': str(e)
            }

    def _clean_text(self, text: str) -> str:
        """Очистка текста от лишних символов и нормализация"""
        # Удаление лишних пробелов и переносов
        text = re.sub(r'\s+', ' ', text.strip())

        # Нормализация пунктуации
        text = re.sub(r'[^\w\s\?\!\.\,\-]', ' ', text)

        return text.lower()

    def _detect_intent(self, text: str) -> Dict[str, Any]:
        """Определение основного интента сообщения"""
        intent_scores = {}

        # Проверка каждого паттерна интента
        for intent, patterns in self.intent_patterns.items():
            score = 0
            matched_patterns = []

            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                if matches > 0:
                    score += matches
                    matched_patterns.append(pattern)

            if score > 0:
                intent_scores[intent] = {
                    'score': score,
                    'patterns': matched_patterns
                }

        # Выбор лучшего интента
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1]['score'])
            confidence = min(best_intent[1]['score'] / 3.0, 1.0)  # Нормализация
            return {
                'intent': best_intent[0],
                'confidence': confidence,
                'matched_patterns': best_intent[1]['patterns']
            }

        return {
            'intent': 'general',
            'confidence': 0.1,
            'matched_patterns': []
        }

    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Извлечение именованных сущностей"""
        entities = []

        # Поиск по паттернам
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        'type': entity_type,
                        'value': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.8
                    })

        # Если доступен spaCy, используем его для NER
        if SPACY_AVAILABLE and nlp:
            try:
                doc = nlp(text)
                for ent in doc.ents:
                    entity_type = self._map_spacy_label(ent.label_)
                    if entity_type:
                        entities.append({
                            'type': entity_type,
                            'value': ent.text,
                            'start': ent.start_char,
                            'end': ent.end_char,
                            'confidence': 0.9
                        })
            except Exception as e:
                logger.warning(f"⚠️ Ошибка spaCy NER: {e}")

        # Удаление дубликатов
        unique_entities = []
        seen_values = set()

        for entity in entities:
            key = (entity['type'], entity['value'].lower())
            if key not in seen_values:
                seen_values.add(key)
                unique_entities.append(entity)

        return unique_entities[:10]  # Ограничение количества сущностей

    def _map_spacy_label(self, spacy_label: str) -> str:
        """Маппинг меток spaCy на наши типы сущностей"""
        label_mapping = {
            'ORG': 'organization',
            'PERSON': 'person',
            'LOC': 'location',
            'GPE': 'location',
            'DATE': 'date',
            'TIME': 'time',
            'MONEY': 'money',
            'PRODUCT': 'product'
        }
        return label_mapping.get(spacy_label)

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Анализ тональности текста"""
        words = text.split()

        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)

        total_words = len(words)
        if total_words == 0:
            return {'sentiment': 'neutral', 'score': 0.0}

        # Расчет оценки
        score = (positive_count - negative_count) / total_words

        # Определение тональности
        if score > 0.1:
            sentiment = 'positive'
        elif score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

        return {
            'sentiment': sentiment,
            'score': score,
            'positive_words': positive_count,
            'negative_words': negative_count
        }

    def _assess_urgency(self, text: str) -> str:
        """Оценка срочности сообщения"""
        urgency_patterns = [
            r'срочно', r'немедленно', r'пожалуйста помогите', r'проблема',
            r'не работает', r'ошибка', r'urgent', r'asap', r'immediately'
        ]

        urgency_score = sum(1 for pattern in urgency_patterns
                           if re.search(pattern, text, re.IGNORECASE))

        if urgency_score >= 2:
            return 'high'
        elif urgency_score >= 1:
            return 'medium'
        else:
            return 'normal'

    def _extract_keywords(self, text: str) -> List[str]:
        """Извлечение ключевых слов"""
        # Простая реализация - можно улучшить с помощью TF-IDF или RAKE
        stop_words = {
            'и', 'в', 'на', 'с', 'по', 'для', 'о', 'об', 'от', 'до', 'у', 'к', 'из',
            'что', 'как', 'где', 'когда', 'почему', 'зачем', 'кто', 'чей',
            'это', 'тот', 'тот', 'такой', 'таким', 'такая', 'такое',
            'быть', 'был', 'была', 'было', 'будет', 'есть', 'являться',
            'я', 'ты', 'он', 'она', 'оно', 'мы', 'вы', 'они',
            'мой', 'твой', 'его', 'её', 'наш', 'ваш', 'их',
            'свой', 'который', 'которая', 'которое', 'которые'
        }

        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        # Подсчет частотности
        word_freq = Counter(keywords)
        return [word for word, count in word_freq.most_common(10)]

    def _detect_language(self, text: str) -> str:
        """Определение языка текста"""
        # Простая эвристика на основе символов
        russian_chars = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
        text_chars = set(text.lower())

        if len(text_chars & russian_chars) > len(text_chars) * 0.3:
            return 'russian'
        else:
            return 'english'  # По умолчанию

    def _assess_complexity(self, text: str) -> str:
        """Оценка сложности текста"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)

        avg_sentence_length = len(words) / max(len(sentences), 1)
        word_length = sum(len(word) for word in words) / max(len(words), 1)

        # Дополнительные факторы сложности
        has_numbers = bool(re.search(r'\d+', text))
        has_questions = text.count('?') > 0
        has_multiple_sentences = len(sentences) > 2

        complexity_score = 0
        if avg_sentence_length > 15:
            complexity_score += 1
        if word_length > 6:
            complexity_score += 1
        if has_numbers:
            complexity_score += 0.5
        if has_questions:
            complexity_score += 0.5
        if has_multiple_sentences:
            complexity_score += 1

        if complexity_score >= 2.5:
            return 'high'
        elif complexity_score >= 1:
            return 'medium'
        else:
            return 'low'

    def analyze_conversation_context(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        🔍 Анализ контекста всего диалога
        """
        if not messages:
            return {'summary': 'No messages to analyze'}

        try:
            context_analysis = {
                'total_messages': len(messages),
                'user_messages': sum(1 for msg in messages if msg.get('role') == 'user'),
                'assistant_messages': sum(1 for msg in messages if msg.get('role') == 'assistant'),
                'avg_message_length': 0,
                'main_topics': [],
                'conversation_flow': 'normal',
                'user_engagement': 'medium',
                'progress_indicators': []
            }

            # Статистика по сообщениям
            total_length = sum(len(msg.get('content', '')) for msg in messages)
            context_analysis['avg_message_length'] = total_length / len(messages)

            # Анализ тем
            all_keywords = []
            for msg in messages:
                if msg.get('content'):
                    analysis = self.analyze_message(msg['content'])
                    all_keywords.extend(analysis['keywords'])

            # Топ-5 ключевых слов диалога
            keyword_freq = Counter(all_keywords)
            context_analysis['main_topics'] = [word for word, count in keyword_freq.most_common(5)]

            # Анализ потока диалога
            if context_analysis['user_messages'] > context_analysis['assistant_messages'] * 2:
                context_analysis['conversation_flow'] = 'user_dominant'
            elif context_analysis['assistant_messages'] > context_analysis['user_messages'] * 2:
                context_analysis['conversation_flow'] = 'assistant_dominant'

            # Оценка вовлеченности
            avg_response_length = 0
            user_lengths = [len(msg.get('content', '')) for msg in messages if msg.get('role') == 'user']

            if user_lengths:
                avg_response_length = sum(user_lengths) / len(user_lengths)
                if avg_response_length > 100:
                    context_analysis['user_engagement'] = 'high'
                elif avg_response_length < 30:
                    context_analysis['user_engagement'] = 'low'

            return context_analysis

        except Exception as e:
            logger.error(f"❌ Error analyzing conversation context: {e}")
            return {'error': str(e)}