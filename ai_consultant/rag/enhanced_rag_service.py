"""
🚀 Enhanced RAG Service for UnitySphere AI
Advanced Retrieval-Augmented Generation with semantic search, recommendations, and personalization
"""

import os
import json
import logging
import uuid
import asyncio
from typing import List, Dict, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

# ML and Vector Database
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# Django and ML Integration
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User
from django.utils import timezone

# OpenAI Integration
import openai

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')


class AdvancedRAGService:
    """
    🎯 Advanced RAG Service with semantic search, recommendations, and personalization
    """

    def __init__(self):
        # Configuration
        self.embedding_model_name = getattr(settings, 'RAG_EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        self.recommendation_model_name = getattr(settings, 'RECOMMENDATION_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
        self.semantic_search_threshold = getattr(settings, 'SEMANTIC_SEARCH_THRESHOLD', 0.3)
        self.max_results_per_query = getattr(settings, 'MAX_RAG_RESULTS', 10)

        # Initialize models
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        self.recommendation_model = SentenceTransformer(self.recommendation_model_name)

        # Sentiment analysis for user feedback
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
        except:
            self.sentiment_analyzer = None
            logger.warning("⚠️ Sentiment analysis model not available")

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=getattr(settings, 'CHROMA_DB_PATH', './chroma_db_enhanced')
        )

        # Collection definitions with metadata
        self.collections_config = {
            'clubs': {
                'description': 'Club information and descriptions',
                'metadata': {'type': 'club_data', 'priority': 'high'}
            },
            'documentation': {
                'description': 'Platform documentation and guides',
                'metadata': {'type': 'documentation', 'priority': 'medium'}
            },
            'faq': {
                'description': 'Frequently asked questions and answers',
                'metadata': {'type': 'faq', 'priority': 'medium'}
            },
            'user_interactions': {
                'description': 'User interaction history and preferences',
                'metadata': {'type': 'interaction_data', 'priority': 'low'}
            },
            'events': {
                'description': 'Events and announcements',
                'metadata': {'type': 'event_data', 'priority': 'medium'}
            },
            'recommendations': {
                'description': 'Personalized recommendations',
                'metadata': {'type': 'recommendation_data', 'priority': 'high'}
            }
        }

        # Initialize collections
        self.collections = {}
        self._init_collections()

        # Caches
        self.embedding_cache = {}
        self.user_profiles = {}
        self.semantic_cache = {}

        logger.info("🚀 Enhanced RAG Service initialized")

    def _init_collections(self):
        """Initialize all ChromaDB collections"""
        try:
            for collection_name, config in self.collections_config.items():
                try:
                    self.collections[collection_name] = self.chroma_client.get_or_create_collection(
                        name=collection_name,
                        metadata=config['metadata']
                    )
                    logger.info(f"✅ Collection '{collection_name}' initialized")
                except Exception as e:
                    logger.error(f"❌ Error initializing collection '{collection_name}': {e}")

        except Exception as e:
            logger.error(f"❌ Critical error initializing RAG collections: {e}")

    def get_embedding(self, text: str, model_type: str = 'embedding') -> np.ndarray:
        """Get text embedding with caching"""
        cache_key = f"{model_type}_{hash(text)}"
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]

        try:
            if model_type == 'recommendation':
                model = self.recommendation_model
            else:
                model = self.embedding_model

            embedding = model.encode(text, convert_to_numpy=True)
            self.embedding_cache[cache_key] = embedding
            return embedding

        except Exception as e:
            logger.error(f"❌ Error getting embedding: {e}")
            return np.zeros(384)  # Default dimension for MiniLM

    def add_document_enhanced(self, collection_name: str, text: str,
                            metadata: Dict[str, Any] = None, user_id: int = None) -> bool:
        """Add document with enhanced metadata and user context"""
        if collection_name not in self.collections:
            logger.error(f"❌ Unknown collection: {collection_name}")
            return False

        try:
            doc_id = str(uuid.uuid4())

            # Enhanced metadata
            enhanced_metadata = {
                'created_at': datetime.now().isoformat(),
                'text_length': len(text),
                'collection': collection_name,
                'word_count': len(text.split()),
                'character_count': len(text),
                'has_questions': '?' in text,
                'has_instructions': any(word in text.lower() for word in ['как', 'как создать', 'инструкция']),
                'language': self._detect_language(text),
                'keywords': self._extract_keywords(text),
                'entities': self._extract_entities(text)
            }

            # Add user context if provided
            if user_id:
                enhanced_metadata.update({
                    'user_id': user_id,
                    'is_personalized': True
                })

            # Add custom metadata
            if metadata:
                enhanced_metadata.update(metadata)

            # Get embedding
            embedding = self.get_embedding(text).tolist()

            # Add to collection
            self.collections[collection_name].add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[enhanced_metadata],
                ids=[doc_id]
            )

            logger.info(f"✅ Enhanced document added to {collection_name}: {doc_id[:8]}...")
            return True

        except Exception as e:
            logger.error(f"❌ Error adding enhanced document: {e}")
            return False

    def semantic_search_enhanced(self, collection_name: str, query: str,
                               n_results: int = 5, user_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Enhanced semantic search with user context and ranking"""
        if collection_name not in self.collections:
            return []

        try:
            # Generate multiple search queries
            search_queries = self._generate_enhanced_queries(query, user_context)

            all_results = []
            for search_query in search_queries:
                results = self._search_single_query(collection_name, search_query, n_results)
                all_results.extend(results)

            # Deduplicate and rank results
            ranked_results = self._rank_and_deduplicate_results(all_results, query, user_context)

            return ranked_results[:n_results]

        except Exception as e:
            logger.error(f"❌ Error in enhanced semantic search: {e}")
            return []

    def _generate_enhanced_queries(self, original_query: str, user_context: Dict[str, Any] = None) -> List[str]:
        """Generate multiple enhanced search queries"""
        queries = [original_query]

        # Extract keywords and create variations
        keywords = self._extract_keywords(original_query)

        # Create keyword-focused queries
        if len(keywords) >= 2:
            keyword_query = " ".join(keywords[:3])
            if keyword_query not in queries:
                queries.append(keyword_query)

        # Add category-specific queries based on user context
        if user_context:
            user_interests = user_context.get('interests', [])
            user_city = user_context.get('city')

            for interest in user_interests[:2]:
                enhanced_query = f"{original_query} для {interest}"
                if enhanced_query not in queries:
                    queries.append(enhanced_query)

            if user_city:
                city_query = f"{original_query} в {user_city}"
                if city_query not in queries:
                    queries.append(city_query)

        # Add intent-specific queries
        intent_queries = self._generate_intent_queries(original_query)
        for intent_query in intent_queries:
            if intent_query not in queries:
                queries.append(intent_query)

        return queries[:5]  # Limit to 5 queries

    def _generate_intent_queries(self, query: str) -> List[str]:
        """Generate intent-specific search queries"""
        intent_patterns = {
            'creation': ['как создать', 'создание', 'основать', 'зарегистрировать'],
            'search': ['найти', 'поиск', 'где найти', 'как найти'],
            'help': ['помощь', 'помогите', 'что делать', 'как решить'],
            'information': ['расскажи', 'что такое', 'информация', 'описание']
        }

        queries = []
        query_lower = query.lower()

        for intent, patterns in intent_patterns.items():
            for pattern in patterns:
                if pattern in query_lower:
                    # Replace with related terms
                    for related in patterns:
                        if related != pattern:
                            enhanced = query_lower.replace(pattern, related)
                            queries.append(enhanced)
                    break

        return queries

    def _search_single_query(self, collection_name: str, query: str, n_results: int) -> List[Dict[str, Any]]:
        """Search in a single query"""
        try:
            query_embedding = self.get_embedding(query).tolist()

            results = self.collections[collection_name].query(
                query_embeddings=[query_embedding],
                n_results=min(n_results * 2, 20),  # Get more results for ranking
                where={
                    'collection': collection_name
                }
            )

            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else 0,
                    'query_matched': query
                })

            return formatted_results

        except Exception as e:
            logger.error(f"❌ Error in single query search: {e}")
            return []

    def _rank_and_deduplicate_results(self, results: List[Dict[str, Any]], query: str,
                                    user_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Rank and deduplicate search results"""
        if not results:
            return []

        # Deduplicate by text similarity
        unique_results = self._deduplicate_by_similarity(results)

        # Calculate ranking scores
        scored_results = []
        query_embedding = self.get_embedding(query)

        for result in unique_results:
            score = self._calculate_ranking_score(result, query_embedding, query, user_context)
            scored_results.append({
                'result': result,
                'score': score
            })

        # Sort by score (higher is better)
        scored_results.sort(key=lambda x: x['score'], reverse=True)

        # Return ranked results
        return [item['result'] for item in scored_results]

    def _deduplicate_by_similarity(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate results based on text similarity"""
        if len(results) <= 1:
            return results

        unique_results = []
        seen_texts = set()

        for result in results:
            text = result['text'].lower().strip()
            text_hash = hash(text[:100])  # Hash first 100 chars

            if text_hash not in seen_texts and len(text) > 20:
                seen_texts.add(text_hash)
                unique_results.append(result)

        return unique_results

    def _calculate_ranking_score(self, result: Dict[str, Any], query_embedding: np.ndarray,
                               query: str, user_context: Dict[str, Any] = None) -> float:
        """Calculate ranking score for a result"""
        score = 0.0

        # Base similarity score (inverse of distance)
        distance = result.get('distance', 1.0)
        similarity = max(0.0, 1.0 - distance)
        score += similarity * 0.4

        # Metadata-based scoring
        metadata = result.get('metadata', {})

        # Recency bonus
        created_at = metadata.get('created_at')
        if created_at:
            try:
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                days_old = (datetime.now() - created_date.replace(tzinfo=None)).days
                recency_bonus = max(0.0, 1.0 - (days_old / 365))  # Decay over 1 year
                score += recency_bonus * 0.2
            except:
                pass

        # User context personalization
        if user_context:
            user_city = user_context.get('city')
            user_interests = user_context.get('interests', [])

            # Location relevance
            if user_city and user_city.lower() in result['text'].lower():
                score += 0.15

            # Interest relevance
            for interest in user_interests:
                if interest.lower() in result['text'].lower():
                    score += 0.1
                    break

        # Content quality indicators
        text_length = len(result['text'])
        if 100 <= text_length <= 1000:  # Good length
            score += 0.1
        elif text_length > 1000:  # Very long content
            score += 0.05

        # Query term matching
        query_words = set(query.lower().split())
        text_words = set(result['text'].lower().split())
        overlap = len(query_words & text_words)
        if overlap > 0:
            keyword_match = overlap / len(query_words)
            score += keyword_match * 0.15

        return score

    def get_personalized_recommendations(self, user_id: int, query: str = None,
                                       category: str = None, n_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Get personalized recommendations for user"""
        try:
            # Get user profile
            user_profile = self._get_or_create_user_profile(user_id)

            # Generate recommendations based on user history and preferences
            recommendations = []

            # 1. Content-based recommendations
            if user_profile.get('recent_interactions'):
                content_recs = self._get_content_based_recommendations(
                    user_profile['recent_interactions'], category, n_recommendations // 2
                )
                recommendations.extend(content_recs)

            # 2. Collaborative filtering recommendations
            collab_recs = self._get_collaborative_recommendations(user_id, category, n_recommendations // 2)
            recommendations.extend(collab_recs)

            # 3. Query-based recommendations
            if query:
                query_recs = self._get_query_based_recommendations(query, user_id, n_recommendations // 2)
                recommendations.extend(query_recs)

            # Deduplicate and rank
            unique_recs = self._deduplicate_recommendations(recommendations)
            ranked_recs = self._rank_recommendations(unique_recs, user_profile)

            return ranked_recs[:n_recommendations]

        except Exception as e:
            logger.error(f"❌ Error getting recommendations: {e}")
            return []

    def _get_or_create_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Get or create user profile"""
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]

        try:
            # Get user data from Django models
            from clubs.models import UserInteraction, ClubInterest
            from django.contrib.auth.models import User

            user = User.objects.get(id=user_id)
            profile = {
                'user_id': user_id,
                'username': user.username,
                'recent_interactions': [],
                'interests': [],
                'preferred_categories': [],
                'interaction_history': []
            }

            # Get recent interactions
            interactions = UserInteraction.objects.filter(user=user).order_by('-created_at')[:10]
            for interaction in interactions:
                profile['recent_interactions'].append({
                    'type': interaction.interaction_type,
                    'content': interaction.content,
                    'timestamp': interaction.created_at.isoformat()
                })

            # Get interests
            interests = ClubInterest.objects.filter(user=user)
            profile['interests'] = [interest.name for interest in interests]

            self.user_profiles[user_id] = profile
            return profile

        except Exception as e:
            logger.error(f"❌ Error creating user profile: {e}")
            return {'user_id': user_id, 'recent_interactions': [], 'interests': []}

    def _get_content_based_recommendations(self, interactions: List[Dict], category: str = None,
                                         n_recs: int = 3) -> List[Dict[str, Any]]:
        """Get content-based recommendations"""
        recommendations = []

        try:
            # Search for similar content based on user's interaction history
            for interaction in interactions[:3]:  # Use last 3 interactions
                content = interaction.get('content', '')
                if content:
                    similar_docs = self.semantic_search_enhanced(
                        'clubs', content, n_results=2
                    )
                    recommendations.extend(similar_docs)

        except Exception as e:
            logger.error(f"❌ Error in content-based recommendations: {e}")

        return recommendations[:n_recs]

    def _get_collaborative_recommendations(self, user_id: int, category: str = None,
                                         n_recs: int = 3) -> List[Dict[str, Any]]:
        """Get collaborative filtering recommendations"""
        recommendations = []

        try:
            # Find similar users and recommend what they liked
            # This is a simplified version - in production, you'd use more sophisticated algorithms
            from clubs.models import UserInteraction, Club

            # Get clubs that similar users interacted with
            user_interactions = UserInteraction.objects.filter(
                user__id=user_id
            ).values_list('content', flat=True)

            if user_interactions:
                # Find other users with similar interactions
                similar_users = UserInteraction.objects.filter(
                    content__in=user_interactions
                ).exclude(user__id=user_id).values_list('user_id', flat=True).distinct()[:5]

                # Get clubs these users liked
                clubs_liked = Club.objects.filter(
                    userinteraction__user_id__in=similar_users
                ).distinct()[:n_recs]

                for club in clubs_liked:
                    recommendations.append({
                        'id': f"club_{club.id}",
                        'text': f"Клуб: {club.name}\nОписание: {club.description}",
                        'metadata': {
                            'type': 'club_recommendation',
                            'club_id': club.id,
                            'club_name': club.name
                        }
                    })

        except Exception as e:
            logger.error(f"❌ Error in collaborative recommendations: {e}")

        return recommendations[:n_recs]

    def _get_query_based_recommendations(self, query: str, user_id: int,
                                       n_recs: int = 3) -> List[Dict[str, Any]]:
        """Get query-based recommendations"""
        try:
            return self.semantic_search_enhanced('clubs', query, n_results=n_recs)
        except Exception as e:
            logger.error(f"❌ Error in query-based recommendations: {e}")
            return []

    def _deduplicate_recommendations(self, recommendations: List[Dict]) -> List[Dict[str, Any]]:
        """Deduplicate recommendations"""
        seen_ids = set()
        unique_recs = []

        for rec in recommendations:
            rec_id = rec.get('id', rec.get('metadata', {}).get('club_id', str(hash(rec.get('text', '')))))
            if rec_id not in seen_ids:
                seen_ids.add(rec_id)
                unique_recs.append(rec)

        return unique_recs

    def _rank_recommendations(self, recommendations: List[Dict], user_profile: Dict) -> List[Dict[str, Any]]:
        """Rank recommendations based on user preferences"""
        ranked_recs = []

        for rec in recommendations:
            score = 0.0
            metadata = rec.get('metadata', {})

            # Category match
            if user_profile.get('preferred_categories'):
                rec_category = metadata.get('category', '').lower()
                for user_cat in user_profile['preferred_categories']:
                    if user_cat.lower() in rec_category:
                        score += 0.3
                        break

            # Interest match
            user_interests = user_profile.get('interests', [])
            rec_text = rec.get('text', '').lower()
            for interest in user_interests:
                if interest.lower() in rec_text:
                    score += 0.2
                    break

            # Recency bonus
            if 'created' in metadata or 'updated' in metadata:
                score += 0.1

            ranked_recs.append({
                'recommendation': rec,
                'score': score
            })

        # Sort by score
        ranked_recs.sort(key=lambda x: x['score'], reverse=True)
        return [item['recommendation'] for item in ranked_recs]

    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze user query intent"""
        intent_analysis = {
            'primary_intent': 'general',
            'confidence': 0.5,
            'intents': {},
            'entities': [],
            'keywords': []
        }

        try:
            # Intent classification
            intent_patterns = {
                'club_creation': ['создать', 'создание', 'основать', 'зарегистрировать', 'новый клуб'],
                'club_search': ['найти', 'поиск', 'где', 'какой', 'показать'],
                'join_club': ['вступить', 'присоединиться', 'вступлю', 'хочу в'],
                'get_help': ['помощь', 'помогите', 'что делать', 'как', 'почему'],
                'event_info': ['мероприятие', 'событие', 'фестиваль', 'конференция'],
                'general_info': ['что такое', 'расскажи', 'информация', 'о чем']
            }

            query_lower = query.lower()
            intent_scores = {}

            for intent, patterns in intent_patterns.items():
                score = sum(1 for pattern in patterns if pattern in query_lower)
                intent_scores[intent] = score / len(patterns)
                intent_analysis['intents'][intent] = score / len(patterns)

            # Determine primary intent
            if intent_scores:
                primary_intent = max(intent_scores.items(), key=lambda x: x[1])
                if primary_intent[1] > 0:
                    intent_analysis['primary_intent'] = primary_intent[0]
                    intent_analysis['confidence'] = primary_intent[1]

            # Extract entities
            intent_analysis['entities'] = self._extract_entities(query)

            # Extract keywords
            intent_analysis['keywords'] = self._extract_keywords(query)

        except Exception as e:
            logger.error(f"❌ Error analyzing query intent: {e}")

        return intent_analysis

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords using TF-IDF approach"""
        try:
            stop_words = set(stopwords.words('russian') + stopwords.words('english'))

            # Simple keyword extraction
            words = re.findall(r'\b[a-zA-Zа-яА-Я]{3,}\b', text.lower())
            filtered_words = [word for word in words if word not in stop_words]

            # Get most frequent words
            word_freq = {}
            for word in filtered_words:
                word_freq[word] = word_freq.get(word, 0) + 1

            # Return top 5 keywords
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in sorted_words[:5]]

        except Exception as e:
            logger.error(f"❌ Error extracting keywords: {e}")
            return []

    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities (simplified)"""
        entities = []

        # Location entities
        locations = ['алматы', 'астана', 'шымкент', 'караганды', 'актау', 'атырау']
        for location in locations:
            if location in text.lower():
                entities.append(f"LOCATION:{location}")

        # Category entities
        categories = ['спорт', 'хобби', 'профессия', 'ит', 'технологии', 'бизнес']
        for category in categories:
            if category in text.lower():
                entities.append(f"CATEGORY:{category}")

        return entities

    def _detect_language(self, text: str) -> str:
        """Detect text language"""
        try:
            # Simple language detection based on Cyrillic characters
            cyrillic_chars = sum(1 for char in text if '\u0400' <= char <= '\u04FF')
            total_chars = len(text.replace(' ', ''))

            if total_chars == 0:
                return 'unknown'

            cyrillic_ratio = cyrillic_chars / total_chars

            if cyrillic_ratio > 0.3:
                return 'russian'
            elif cyrillic_ratio < 0.1:
                return 'english'
            else:
                return 'mixed'
        except:
            return 'unknown'

    def format_enhanced_context(self, query: str, search_results: List[Dict],
                              user_context: Dict[str, Any] = None,
                              recommendations: List[Dict] = None) -> str:
        """Format enhanced context for AI response"""
        context_parts = []

        # Query analysis
        intent_analysis = self.analyze_query_intent(query)
        context_parts.append(f"🔍 **Анализ запроса:** {intent_analysis['primary_intent']} (уверенность: {intent_analysis['confidence']:.2f})")

        # Search results
        if search_results:
            context_parts.append("\n📚 **Найденная информация:**")
            for i, result in enumerate(search_results[:3], 1):
                text = result['text'][:300]
                if len(result['text']) > 300:
                    text += "..."

                metadata = result.get('metadata', {})
                source_info = metadata.get('collection', 'unknown')
                confidence = 1.0 - result.get('distance', 0.5)

                context_parts.append(f"{i}. {text} (Источник: {source_info}, Уверенность: {confidence:.2f})")

        # Recommendations
        if recommendations:
            context_parts.append("\n🎯 **Рекомендации:**")
            for i, rec in enumerate(recommendations[:2], 1):
                text = rec.get('text', '')[:200]
                if len(text) > 200:
                    text += "..."

                context_parts.append(f"{i}. {text}")

        # User context
        if user_context:
            user_info = []
            if user_context.get('city'):
                user_info.append(f"Город: {user_context['city']}")
            if user_context.get('interests'):
                user_info.append(f"Интересы: {', '.join(user_context['interests'][:3])}")

            if user_info:
                context_parts.append(f"\n👤 **Контекст пользователя:** {', '.join(user_info)}")

        # Final context
        context_parts.append(f"\n📌 **Запрос пользователя:** {query}")
        context_parts.append("Используй эту информацию для предоставления персонализированного и точного ответа.")

        return "\n".join(context_parts)

    def rebuild_enhanced_index(self):
        """Rebuild the enhanced RAG index"""
        logger.info("🔄 Rebuilding enhanced RAG index...")

        try:
            # Clear all collections
            for collection_name, collection in self.collections.items():
                if collection:
                    try:
                        collection.delete()
                        logger.info(f"✅ Collection {collection_name} cleared")
                    except Exception as e:
                        logger.error(f"❌ Error clearing {collection_name}: {e}")

            # Reinitialize
            self._init_collections()

            # Index platform knowledge
            self._index_platform_knowledge()

            # Index existing clubs
            self._index_clubs_data()

            # Index documentation
            self._index_documentation_data()

            logger.info("✅ Enhanced RAG index rebuilt successfully")

        except Exception as e:
            logger.error(f"❌ Error rebuilding enhanced index: {e}")

    def _index_platform_knowledge(self):
        """Index platform knowledge base"""
        try:
            from ai_consultant.knowledge.platform_knowledge_base import platform_knowledge

            # Index categories
            for category_key, category_data in platform_knowledge.CATEGORIES.items():
                category_text = f"""
                Категория: {category_data['name']}
                Описание: {category_data['description']}
                Примеры: {', '.join(category_data['examples'][:5])}
                Преимущества: {', '.join(category_data['benefits'][:3])}
                Теги: {', '.join(category_data['search_tags'])}
                """

                self.add_document_enhanced(
                    'documentation',
                    category_text,
                    metadata={
                        'category': category_key,
                        'type': 'category_info',
                        'priority': 'high'
                    }
                )

            # Index instructions
            for instruction_name, instruction_data in platform_knowledge.INSTRUCTIONS.items():
                instruction_text = f"""
                Инструкция: {instruction_data.get('title', instruction_name)}
                Шаги: {', '.join([step.get('title', '') for step in instruction_data.get('steps', [])])}
                Обязательные поля: {', '.join([field.get('name', '') for field in instruction_data.get('required_fields', [])])}
                Советы: {', '.join(instruction_data.get('tips', [])[:3])}
                """

                self.add_document_enhanced(
                    'documentation',
                    instruction_text,
                    metadata={
                        'instruction_name': instruction_name,
                        'type': 'instruction',
                        'priority': 'high'
                    }
                )

            logger.info("✅ Platform knowledge indexed")

        except Exception as e:
            logger.error(f"❌ Error indexing platform knowledge: {e}")

    def _index_clubs_data(self):
        """Index existing club data"""
        try:
            from clubs.models import Club

            clubs = Club.objects.filter(is_active=True)[:50]  # Limit for initial indexing

            for club in clubs:
                club_text = f"""
                Клуб: {club.name}
                Описание: {club.description or 'Нет описания'}
                Категория: {club.category.name if club.category else 'Не указана'}
                Город: {club.city or 'Не указан'}
                Email: {club.email or 'Не указан'}
                Телефон: {club.phone or 'Не указан'}
                """

                self.add_document_enhanced(
                    'clubs',
                    club_text,
                    metadata={
                        'club_id': club.id,
                        'club_name': club.name,
                        'category': club.category.name if club.category else None,
                        'city': club.city,
                        'is_active': club.is_active
                    }
                )

            logger.info(f"✅ Indexed {len(clubs)} clubs")

        except Exception as e:
            logger.error(f"❌ Error indexing clubs: {e}")

    def _index_documentation_data(self):
        """Index documentation and FAQ data"""
        documentation_entries = [
            {
                'text': '''
                UnitySphere - это платформа для управления клубами и мероприятиями.
                Для создания клуба необходимо: заполнить форму, указать название, описание,
                добавить контактную информацию и получить подтверждение от модератора.
                Процесс создания занимает до 24 часов на модерацию.
                ''',
                'metadata': {'type': 'getting_started', 'priority': 'high', 'audience': 'new_users'}
            },
            {
                'text': '''
                Правила создания клуба на UnitySphere:
                1. Уникальное название клуба
                2. Подробное описание деятельности (минимум 200 символов)
                3. Контактная информация (телефон, email)
                4. Выбор категории клуба
                5. Загрузка логотипа клуба
                6. Модерация в течение 24 часов
                7. Обязательные поля: Название, Категория, Описание, Email, Телефон, Город
                ''',
                'metadata': {'type': 'club_creation_rules', 'priority': 'high', 'audience': 'creators'}
            },
            {
                'text': '''
                Frequently Asked Questions:
                Q: Как присоединиться к клубу?
                A: Найдите интересующий клуб, нажмите "Присоединиться" и ожидайте подтверждения администратора.

                Q: Как создать мероприятие?
                A: В личном кабинете клуба выберите "Создать мероприятие", заполните форму и опубликуйте.

                Q: Сколько стоит пользование платформой?
                A: Основной функционал платформы бесплатный для пользователей.
                ''',
                'metadata': {'type': 'faq', 'priority': 'medium', 'audience': 'all_users'}
            }
        ]

        for entry in documentation_entries:
            self.add_document_enhanced('documentation', entry['text'], entry['metadata'])
            self.add_document_enhanced('faq', entry['text'], entry['metadata'])

        logger.info(f"✅ Added {len(documentation_entries)} documentation entries")

    async def semantic_search(self, query: str, collections: List[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        🔍 Multi-collection semantic search for club creation agent
        """
        if collections is None:
            collections = ['clubs', 'categories', 'platform_info', 'documentation']

        try:
            all_results = []

            # Search across multiple collections
            for collection_name in collections:
                if collection_name in self.collections:
                    # Use enhanced search for each collection
                    results = self.semantic_search_enhanced(
                        collection_name=collection_name,
                        query=query,
                        n_results=top_k
                    )

                    # Add collection identifier to results
                    for result in results:
                        result['collection'] = collection_name
                        all_results.append(result)

            # Deduplicate and rank results across all collections
            if all_results:
                # Convert to numpy array for similarity calculations
                query_embedding = self.embedding_model.encode([query])[0]

                for result in all_results:
                    if 'embedding' in result:
                        similarity = cosine_similarity(
                            [query_embedding],
                            [result['embedding']]
                        )[0][0]
                        result['similarity'] = similarity

                # Sort by similarity
                all_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)

            return all_results[:top_k]

        except Exception as e:
            logger.error(f"❌ Error in multi-collection semantic search: {e}")
            return []

    def get_club_creation_context(self, query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        🎯 Get contextual information for club creation
        """
        try:
            # Search for relevant club creation information
            club_results = self.semantic_search_enhanced(
                collection_name='clubs',
                query=query,
                n_results=3,
                user_context=user_context
            )

            # Search for category information
            category_results = self.semantic_search_enhanced(
                collection_name='categories',
                query=query,
                n_results=3,
                user_context=user_context
            )

            # Search for platform rules
            platform_results = self.semantic_search_enhanced(
                collection_name='documentation',
                query=f"{query} создание клуба правила",
                n_results=2,
                user_context=user_context
            )

            return {
                'club_examples': club_results,
                'category_info': category_results,
                'platform_rules': platform_results,
                'query': query,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error getting club creation context: {e}")
            return {
                'club_examples': [],
                'category_info': [],
                'platform_rules': [],
                'query': query,
                'error': str(e)
            }


# Global instance
enhanced_rag_service = None


def get_enhanced_rag_service():
    """Get enhanced RAG service instance"""
    global enhanced_rag_service
    if enhanced_rag_service is None:
        enhanced_rag_service = AdvancedRAGService()
    return enhanced_rag_service