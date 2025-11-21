"""
🔍 RAG (Retrieval-Augmented Generation) Service
Улучшенный сервис для обогащения запросов контекстом из векторной базы знаний
"""

import os
import json
import logging
import uuid
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize

# Загрузка необходимых NLTK данных
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

from django.conf import settings
from django.core.cache import cache
from openai import OpenAI

logger = logging.getLogger(__name__)


class RAGService:
    """
    🚀 Сервис RAG для обогащения контекстом запросов ИИ-консультанта
    """

    def __init__(self):
        self.model_name = getattr(settings, 'RAG_EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        self.embedding_model = SentenceTransformer(self.model_name)
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # Инициализация ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=getattr(settings, 'CHROMA_DB_PATH', './chroma_db')
        )

        # Коллекции для разных типов знаний
        self.collections = {
            'clubs': None,
            'documentation': None,
            'faq': None,
            'history': None,
            'events': None
        }

        # Кэш для эмбеддингов
        self.embedding_cache = {}
        self._init_collections()

    def _init_collections(self):
        """Инициализация коллекций ChromaDB"""
        try:
            for collection_name in self.collections.keys():
                try:
                    self.collections[collection_name] = self.chroma_client.get_or_create_collection(
                        name=collection_name,
                        metadata={"description": f"UnitySphere {collection_name} knowledge base"}
                    )
                    logger.info(f"✅ Коллекция '{collection_name}' инициализирована")
                except Exception as e:
                    logger.error(f"❌ Ошибка инициализации коллекции '{collection_name}': {e}")

        except Exception as e:
            logger.error(f"❌ Критическая ошибка RAG сервиса: {e}")

    def get_embedding(self, text: str) -> np.ndarray:
        """Получение эмбеддинга текста с кэшированием"""
        if text in self.embedding_cache:
            return self.embedding_cache[text]

        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            self.embedding_cache[text] = embedding
            return embedding
        except Exception as e:
            logger.error(f"❌ Ошибка получения эмбеддинга: {e}")
            return np.zeros(384)  # Размерность по умолчанию для MiniLM

    def add_document(self, collection_name: str, text: str, metadata: Dict[str, Any] = None):
        """Добавление документа в векторную базу"""
        if collection_name not in self.collections:
            logger.error(f"❌ Неизвестная коллекция: {collection_name}")
            return False

        try:
            doc_id = str(uuid.uuid4())
            embedding = self.get_embedding(text).tolist()

            # Добавление метаданных
            if metadata is None:
                metadata = {}
            metadata.update({
                'created_at': datetime.now().isoformat(),
                'text_length': len(text),
                'collection': collection_name
            })

            self.collections[collection_name].add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata],
                ids=[doc_id]
            )

            logger.info(f"✅ Документ добавлен в {collection_name}: {doc_id[:8]}...")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка добавления документа: {e}")
            return False

    def search_similar(self, collection_name: str, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Поиск похожих документов в коллекции"""
        if collection_name not in self.collections or not self.collections[collection_name]:
            logger.warning(f"⚠️ Коллекция {collection_name} не доступна")
            return []

        try:
            query_embedding = self.get_embedding(query).tolist()

            results = self.collections[collection_name].query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, 10)
            )

            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else 0
                })

            return formatted_results

        except Exception as e:
            logger.error(f"❌ Ошибка поиска в {collection_name}: {e}")
            return []

    def get_enhanced_context(self, query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        🎯 Получение обогащенного контекста для запроса
        """
        context = {
            'query': query,
            'user_context': user_context or {},
            'retrieved_info': {},
            'confidence_scores': {},
            'total_docs_found': 0
        }

        # Поиск в разных коллекциях
        search_queries = self._generate_search_queries(query)

        for collection_name in self.collections.keys():
            if not self.collections[collection_name]:
                continue

            all_results = []
            for search_query in search_queries:
                results = self.search_similar(collection_name, search_query, n_results=3)
                all_results.extend(results)

            # Удаление дубликатов и ранжирование
            unique_results = self._deduplicate_and_rank(all_results)

            if unique_results:
                context['retrieved_info'][collection_name] = unique_results[:3]  # Топ-3 для каждой коллекции
                context['total_docs_found'] += len(unique_results)

        # Вычисление общей уверенности
        context['overall_confidence'] = self._calculate_overall_confidence(context)

        return context

    def _generate_search_queries(self, original_query: str) -> List[str]:
        """Генерация дополнительных поисковых запросов"""
        queries = [original_query]

        # Простая эвристика для расширения запроса
        keywords = {
            'клуб': ['сообщество', 'объединение', 'группа', 'секция'],
            'создать': ['основать', 'зарегистрировать', 'открыть', 'учредить'],
            'мероприятие': ['событие', 'фестиваль', 'встреча', 'конференция'],
            'вопрос': ['проблема', 'помощь', 'консультация', 'совет']
        }

        for key, synonyms in keywords.items():
            if key.lower() in original_query.lower():
                for synonym in synonyms:
                    expanded_query = original_query.lower().replace(key.lower(), synonym)
                    if expanded_query not in queries:
                        queries.append(expanded_query)

        return queries[:5]  # Максимум 5 запросов

    def _deduplicate_and_rank(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Дедупликация и ранжирование результатов"""
        if not results:
            return []

        # Простая дедупликация по тексту
        seen_texts = set()
        unique_results = []

        for result in results:
            text_lower = result['text'].lower().strip()
            if text_lower not in seen_texts and len(text_lower) > 20:
                seen_texts.add(text_lower)
                unique_results.append(result)

        # Ранжирование по расстоянию (чем меньше, тем лучше)
        unique_results.sort(key=lambda x: x.get('distance', 1.0))

        return unique_results

    def _calculate_overall_confidence(self, context: Dict[str, Any]) -> float:
        """Вычисление общей уверенности в релевантности контекста"""
        if not context['retrieved_info']:
            return 0.0

        total_confidence = 0.0
        total_docs = 0

        for collection_name, docs in context['retrieved_info'].items():
            for doc in docs:
                # Конвертация distance в confidence (1 - normalized_distance)
                distance = doc.get('distance', 1.0)
                confidence = max(0.0, min(1.0, 1.0 - distance))
                total_confidence += confidence
                total_docs += 1

        return total_confidence / total_docs if total_docs > 0 else 0.0

    def format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """
        📝 Форматирование контекста для промпта
        """
        if not context['retrieved_info']:
            return "Релевантная информация не найдена. Ответь на основе общих знаний о платформе UnitySphere."

        formatted_sections = []

        for collection_name, docs in context['retrieved_info'].items():
            if not docs:
                continue

            section_title = {
                'clubs': '🏢 Информация о клубах',
                'documentation': '📚 Документация платформы',
                'faq': '❓ Частые вопросы',
                'history': '💬 История консультаций',
                'events': '📅 Мероприятия и события'
            }.get(collection_name, f'📄 {collection_name.title()}')

            section_content = f"**{section_title}:**\n"

            for i, doc in enumerate(docs, 1):
                # Ограничение длины текста
                text = doc['text'][:500]
                if len(doc['text']) > 500:
                    text += "..."

                relevance_score = 1.0 - doc.get('distance', 0.5)
                section_content += f"{i}. {text} (Релевантность: {relevance_score:.2f})\n"

            formatted_sections.append(section_content)

        # Общая уверенность
        overall_conf = context.get('overall_confidence', 0.0)
        confidence_text = f"**Общая уверенность в релевантности: {overall_conf:.2f}**"

        # Сборка итогового контекста
        final_context = f"""
🔍 **Контекст из базы знаний UnitySphere:**

{chr(10).join(formatted_sections)}

{confidence_text}

Используй эту информацию для предоставления точного и contextual ответа пользователю.
"""

        return final_context

    def index_club_data(self):
        """Индексация данных о клубах"""
        try:
            from clubs.models import Club

            clubs = Club.objects.filter(is_active=True)[:100]  # Ограничение для начала

            for club in clubs:
                # Создание текстового представления клуба
                club_text = f"""
                Клуб: {club.name}
                Описание: {club.description or 'Нет описания'}
                Категория: {club.category.name if club.category else 'Не указана'}
                Телефон: {club.phone or 'Не указан'}
                Email: {club.email or 'Не указан'}
                """

                metadata = {
                    'club_id': club.id,
                    'club_name': club.name,
                    'category': club.category.name if club.category else None,
                    'is_active': club.is_active
                }

                self.add_document('clubs', club_text.strip(), metadata)

            logger.info(f"✅ Проиндексировано клубов: {len(clubs)}")

        except Exception as e:
            logger.error(f"❌ Ошибка индексации клубов: {e}")

    def index_documentation(self):
        """Индексация документации платформы"""
        docs_to_add = [
            {
                'text': '''
                UnitySphere - это платформа для управления клубами и мероприятиями.
                Для создания клуба необходимо: заполнить форму, указать название, описание,
                добавить контактную информацию и получить подтверждение от модератора.
                ''',
                'metadata': {'type': 'getting_started', 'priority': 'high'}
            },
            {
                'text': '''
                Правила создания клуба на UnitySphere:
                1. Уникальное название клуба
                2. Подробное описание деятельности
                3. Контактная информация (телефон, email)
                4. Выбор категории клуба
                5. Загрузка логотипа клуба
                6. Модерация в течение 24 часов
                ''',
                'metadata': {'type': 'club_creation_rules', 'priority': 'high'}
            },
            {
                'text': '''
                Frequently Asked Questions:
                Q: Как присоединиться к клубу?
                A: Найдите интересующий клуб, нажмите "Присоединиться" и ожидайте подтверждения.

                Q: Как создать мероприятие?
                A: В личном кабинете клуба выберите "Создать мероприятие", заполните форму и опубликуйте.
                ''',
                'metadata': {'type': 'faq', 'priority': 'medium'}
            }
        ]

        for doc in docs_to_add:
            self.add_document('documentation', doc['text'], doc['metadata'])
            self.add_document('faq', doc['text'], doc['metadata'])

        logger.info(f"✅ Добавлено документов: {len(docs_to_add)}")

    def rebuild_index(self):
        """Перестроение индекса с нуля"""
        logger.info("🔄 Перестроение индекса RAG...")

        # Очистка коллекций
        for collection_name, collection in self.collections.items():
            if collection:
                try:
                    collection.delete()
                    logger.info(f"✅ Коллекция {collection_name} очищена")
                except Exception as e:
                    logger.error(f"❌ Ошибка очистки {collection_name}: {e}")

        # Переинициализация
        self._init_collections()

        # Индексация данных
        self.index_documentation()
        self.index_club_data()

        logger.info("✅ Перестроение индекса завершено")


# Глобальный экземпляр RAG сервиса
rag_service = None


def get_rag_service():
    """Получение экземпляра RAG сервиса"""
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    return rag_service