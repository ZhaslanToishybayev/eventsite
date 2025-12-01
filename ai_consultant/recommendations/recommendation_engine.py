"""
🎯 Advanced Recommendation Engine for UnitySphere AI
Personalized recommendations using collaborative filtering, content-based filtering, and deep learning
"""

import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict, Counter
import json

# Machine Learning
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.decomposition import NMF
import networkx as nx

# Django Integration
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User
from django.utils import timezone

# AI/ML Models
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    🚀 Advanced Recommendation Engine with multiple algorithms
    """

    def __init__(self):
        # Configuration
        self.recommendation_models = {}
        self.user_profiles = {}
        self.club_embeddings = {}
        self.similarity_matrices = {}

        # ML Models
        self.content_vectorizer = TfidfVectorizer(max_features=1000, stop_words='russian')
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Recommendation weights
        self.weights = {
            'content': 0.3,
            'collaborative': 0.3,
            'demographic': 0.2,
            'contextual': 0.2
        }

        # Cache settings
        self.cache_timeout = 3600  # 1 hour
        self.max_recommendations = 20

        logger.info("🎯 Recommendation Engine initialized")

    async def get_personalized_recommendations(self, user_id: int, context: Dict[str, Any] = None,
                                             n_recommendations: int = 5) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations for user
        """
        try:
            # Get user profile
            user_profile = await self._get_user_profile(user_id)

            # Get different types of recommendations
            recommendations = {}

            # 1. Content-based recommendations
            content_recs = await self._get_content_recommendations(user_profile, context)
            recommendations['content'] = content_recs

            # 2. Collaborative filtering
            collaborative_recs = await self._get_collaborative_recommendations(user_profile, context)
            recommendations['collaborative'] = collaborative_recs

            # 3. Demographic recommendations
            demographic_recs = await self._get_demographic_recommendations(user_profile, context)
            recommendations['demographic'] = demographic_recs

            # 4. Contextual recommendations
            contextual_recs = await self._get_contextual_recommendations(user_profile, context)
            recommendations['contextual'] = contextual_recs

            # Combine and rank recommendations
            final_recommendations = self._combine_recommendations(recommendations, context)

            return final_recommendations[:n_recommendations]

        except Exception as e:
            logger.error(f"❌ Error getting recommendations: {e}")
            return await self._get_fallback_recommendations(context, n_recommendations)

    async def _get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user profile"""
        cache_key = f"user_profile_{user_id}"
        cached_profile = cache.get(cache_key)

        if cached_profile:
            return cached_profile

        try:
            from clubs.models import Club, UserInteraction, ClubInterest, UserPreference
            from django.contrib.auth.models import User

            user = User.objects.get(id=user_id)

            # Get user interactions
            interactions = UserInteraction.objects.filter(user=user).order_by('-created_at')[:50]
            interaction_data = [
                {
                    'type': interaction.interaction_type,
                    'content': interaction.content,
                    'club_id': getattr(interaction, 'club_id', None),
                    'timestamp': interaction.created_at.isoformat()
                }
                for interaction in interactions
            ]

            # Get user interests
            interests = ClubInterest.objects.filter(user=user)
            user_interests = [interest.name for interest in interests]

            # Get user preferences
            preferences = UserPreference.objects.filter(user=user).first()
            preference_data = {}
            if preferences:
                preference_data = {
                    'preferred_categories': preferences.preferred_categories,
                    'preferred_city': preferences.preferred_city,
                    'age_group': preferences.age_group,
                    'activity_level': preferences.activity_level
                }

            # Analyze user behavior patterns
            behavior_analysis = self._analyze_user_behavior(interaction_data)

            profile = {
                'user_id': user_id,
                'username': user.username,
                'email': user.email,
                'interactions': interaction_data,
                'interests': user_interests,
                'preferences': preference_data,
                'behavior': behavior_analysis,
                'created_at': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            }

            # Cache profile
            cache.set(cache_key, profile, self.cache_timeout)
            return profile

        except Exception as e:
            logger.error(f"❌ Error getting user profile: {e}")
            return {'user_id': user_id, 'interactions': [], 'interests': []}

    def _analyze_user_behavior(self, interactions: List[Dict]) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        if not interactions:
            return {}

        # Count interaction types
        interaction_types = Counter([inter['type'] for inter in interactions])

        # Analyze timing patterns
        recent_interactions = [inter for inter in interactions
                             if datetime.fromisoformat(inter['timestamp']) > datetime.now() - timedelta(days=30)]

        # Identify preferred categories
        club_ids = [inter['club_id'] for inter in interactions if inter.get('club_id')]
        if club_ids:
            from clubs.models import Club
            clubs = Club.objects.filter(id__in=club_ids)
            categories = Counter([club.category.name for club in clubs if club.category])

        return {
            'total_interactions': len(interactions),
            'recent_interactions': len(recent_interactions),
            'interaction_types': dict(interaction_types),
            'preferred_categories': dict(categories) if club_ids else {},
            'engagement_score': min(len(recent_interactions) / 10, 1.0)  # Normalize to 0-1
        }

    async def _get_content_recommendations(self, user_profile: Dict[str, Any],
                                         context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get content-based recommendations"""
        try:
            from clubs.models import Club

            # Get user's liked content
            user_interactions = user_profile.get('interactions', [])
            liked_clubs = [inter['club_id'] for inter in user_interactions
                          if inter.get('club_id') and inter.get('type') in ['like', 'join', 'view']]

            if not liked_clubs:
                return []

            # Get club content
            liked_clubs_data = Club.objects.filter(id__in=liked_clubs)
            all_clubs = Club.objects.filter(is_active=True).exclude(id__in=liked_clubs)[:100]

            if not all_clubs:
                return []

            # Create content vectors
            liked_content = []
            for club in liked_clubs_data:
                content = f"{club.name} {club.description} {club.category.name if club.category else ''}"
                liked_content.append(content)

            all_content = []
            all_club_ids = []
            for club in all_clubs:
                content = f"{club.name} {club.description} {club.category.name if club.category else ''}"
                all_content.append(content)
                all_club_ids.append(club.id)

            # Calculate similarities
            if liked_content and all_content:
                liked_vector = self.sentence_model.encode(liked_content, convert_to_tensor=True)
                all_vectors = self.sentence_model.encode(all_content, convert_to_tensor=True)

                # Calculate cosine similarities
                similarities = cosine_similarity(
                    self.sentence_model.encode(liked_content).mean(axis=0).reshape(1, -1),
                    self.sentence_model.encode(all_content)
                )

                # Get top recommendations
                top_indices = similarities[0].argsort()[-10:][::-1]
                recommendations = []

                for idx in top_indices:
                    if similarities[0][idx] > 0.3:  # Similarity threshold
                        club = all_clubs[idx]
                        recommendations.append({
                            'club_id': club.id,
                            'score': float(similarities[0][idx]),
                            'reason': 'Similar content to your interests',
                            'type': 'content'
                        })

                return recommendations

        except Exception as e:
            logger.error(f"❌ Error in content recommendations: {e}")

        return []

    async def _get_collaborative_recommendations(self, user_profile: Dict[str, Any],
                                               context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get collaborative filtering recommendations"""
        try:
            from clubs.models import Club, UserInteraction

            user_id = user_profile['user_id']
            user_interactions = user_profile.get('interactions', [])

            if not user_interactions:
                return []

            # Find similar users
            user_clubs = {inter['club_id'] for inter in user_interactions if inter.get('club_id')}
            if not user_clubs:
                return []

            # Get users who interacted with same clubs
            similar_users_data = UserInteraction.objects.filter(
                club_id__in=user_clubs
            ).exclude(user_id=user_id).values('user_id', 'club_id')

            # Create user-club matrix
            user_club_matrix = defaultdict(set)
            for data in similar_users_data:
                user_club_matrix[data['user_id']].add(data['club_id'])

            if not user_club_matrix:
                return []

            # Find most similar users (Jaccard similarity)
            user_similarities = []
            for similar_user_id, clubs in user_club_matrix.items():
                intersection = len(user_clubs & clubs)
                union = len(user_clubs | clubs)
                similarity = intersection / union if union > 0 else 0

                if similarity > 0.1:  # Minimum similarity threshold
                    user_similarities.append((similar_user_id, similarity))

            # Get recommendations from similar users
            user_similarities.sort(key=lambda x: x[1], reverse=True)
            top_similar_users = [user_id for user_id, _ in user_similarities[:5]]

            if not top_similar_users:
                return []

            # Get clubs that similar users liked but current user hasn't seen
            recommended_clubs = UserInteraction.objects.filter(
                user_id__in=top_similar_users
            ).exclude(
                club_id__in=user_clubs
            ).values('club_id').annotate(
                score=Count('id')
            ).order_by('-score')[:10]

            recommendations = []
            for club_data in recommended_clubs:
                try:
                    club = Club.objects.get(id=club_data['club_id'])
                    recommendations.append({
                        'club_id': club.id,
                        'score': float(club_data['score'] / len(top_similar_users)),
                        'reason': 'Users with similar interests liked this',
                        'type': 'collaborative'
                    })
                except Club.DoesNotExist:
                    continue

            return recommendations

        except Exception as e:
            logger.error(f"❌ Error in collaborative recommendations: {e}")

        return []

    async def _get_demographic_recommendations(self, user_profile: Dict[str, Any],
                                             context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get demographic-based recommendations"""
        try:
            from clubs.models import Club, User, UserPreference

            user_id = user_profile['user_id']
            preferences = user_profile.get('preferences', {})

            # Build demographic filter
            demographic_filter = {}

            if preferences.get('preferred_city'):
                demographic_filter['city'] = preferences['preferred_city']

            if preferences.get('age_group'):
                # Map age group to appropriate clubs
                age_group = preferences['age_group']
                if age_group in ['young_adult', 'adult']:
                    demographic_filter['age_friendly'] = True

            # Get popular clubs in demographic segment
            if demographic_filter:
                clubs = Club.objects.filter(is_active=True, **demographic_filter)[:10]
            else:
                # Get overall popular clubs
                clubs = Club.objects.filter(is_active=True)[:10]

            recommendations = []
            for club in clubs:
                # Calculate popularity score
                interaction_count = club.userinteraction_set.count()
                popularity_score = min(interaction_count / 100, 1.0)  # Normalize

                recommendations.append({
                    'club_id': club.id,
                    'score': popularity_score,
                    'reason': 'Popular in your demographic',
                    'type': 'demographic'
                })

            return sorted(recommendations, key=lambda x: x['score'], reverse=True)

        except Exception as e:
            logger.error(f"❌ Error in demographic recommendations: {e}")

        return []

    async def _get_contextual_recommendations(self, user_profile: Dict[str, Any],
                                            context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get context-aware recommendations"""
        try:
            from clubs.models import Club

            recommendations = []
            current_time = datetime.now()

            # Time-based recommendations
            hour = current_time.hour
            if 18 <= hour <= 22:  # Evening - social activities
                clubs = Club.objects.filter(
                    is_active=True,
                    category__name__in=['Хобби', 'Спорт']
                )[:5]
            elif 9 <= hour <= 17:  # Daytime - professional
                clubs = Club.objects.filter(
                    is_active=True,
                    category__name__in=['Профессия', 'IT']
                )[:5]
            else:  # Late night/early morning
                clubs = Club.objects.filter(
                    is_active=True,
                    category__name='IT'
                )[:5]

            for club in clubs:
                recommendations.append({
                    'club_id': club.id,
                    'score': 0.7,
                    'reason': 'Recommended for current time',
                    'type': 'contextual'
                })

            # Context-based filtering
            if context:
                # Location-based
                if context.get('city'):
                    location_clubs = Club.objects.filter(
                        is_active=True,
                        city=context['city']
                    )[:3]

                    for club in location_clubs:
                        recommendations.append({
                            'club_id': club.id,
                            'score': 0.8,
                            'reason': 'Near your location',
                            'type': 'contextual'
                        })

                # Interest-based from context
                if context.get('interests'):
                    interest_clubs = Club.objects.filter(
                        is_active=True,
                        category__name__in=context['interests']
                    )[:3]

                    for club in interest_clubs:
                        recommendations.append({
                            'club_id': club.id,
                            'score': 0.9,
                            'reason': 'Matches your interests',
                            'type': 'contextual'
                        })

            return sorted(recommendations, key=lambda x: x['score'], reverse=True)

        except Exception as e:
            logger.error(f"❌ Error in contextual recommendations: {e}")

        return []

    def _combine_recommendations(self, recommendations: Dict[str, Any],
                               context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Combine recommendations from different sources"""
        all_recommendations = []

        for rec_type, rec_list in recommendations.items():
            weight = self.weights.get(rec_type, 0.1)

            for rec in rec_list:
                # Apply weight to score
                weighted_score = rec['score'] * weight

                # Add diversity bonus
                diversity_bonus = self._calculate_diversity_bonus(rec, all_recommendations)
                final_score = weighted_score + diversity_bonus

                all_recommendations.append({
                    'club_id': rec['club_id'],
                    'score': final_score,
                    'reason': rec['reason'],
                    'type': rec['type'],
                    'weighted_score': weighted_score,
                    'diversity_bonus': diversity_bonus
                })

        # Remove duplicates (keep highest scoring)
        unique_recommendations = {}
        for rec in all_recommendations:
            club_id = rec['club_id']
            if club_id not in unique_recommendations or rec['score'] > unique_recommendations[club_id]['score']:
                unique_recommendations[club_id] = rec

        # Sort by final score
        sorted_recommendations = sorted(
            unique_recommendations.values(),
            key=lambda x: x['score'],
            reverse=True
        )

        return sorted_recommendations

    def _calculate_diversity_bonus(self, recommendation: Dict[str, Any],
                                 existing_recommendations: List[Dict[str, Any]]) -> float:
        """Calculate diversity bonus for recommendation"""
        if not existing_recommendations:
            return 0.1  # First recommendation gets diversity bonus

        club_id = recommendation['club_id']
        rec_type = recommendation['type']

        # Check diversity in categories and types
        diversity_score = 0.0

        # Category diversity
        try:
            from clubs.models import Club
            club = Club.objects.get(id=club_id)
            club_category = club.category.name if club.category else 'Other'

            existing_categories = set()
            for rec in existing_recommendations:
                try:
                    existing_club = Club.objects.get(id=rec['club_id'])
                    existing_categories.add(existing_club.category.name if existing_club.category else 'Other')
                except Club.DoesNotExist:
                    continue

            if club_category not in existing_categories:
                diversity_score += 0.05

        except Exception:
            pass

        # Type diversity
        existing_types = {rec['type'] for rec in existing_recommendations}
        if rec_type not in existing_types:
            diversity_score += 0.02

        return diversity_score

    async def _get_fallback_recommendations(self, context: Dict[str, Any] = None,
                                          n_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Get fallback recommendations when other methods fail"""
        try:
            from clubs.models import Club

            # Get trending/popular clubs
            clubs = Club.objects.filter(is_active=True).order_by('-created_at')[:n_recommendations]

            recommendations = []
            for i, club in enumerate(clubs):
                recommendations.append({
                    'club_id': club.id,
                    'score': 0.5 - (i * 0.1),  # Decreasing score
                    'reason': 'Recently created club',
                    'type': 'fallback'
                })

            return recommendations

        except Exception as e:
            logger.error(f"❌ Error in fallback recommendations: {e}")
            return []

    async def update_user_recommendation_feedback(self, user_id: int, club_id: int,
                                                action: str, rating: float = None) -> bool:
        """
        Update recommendation system with user feedback
        """
        try:
            from clubs.models import UserInteraction

            # Record interaction
            UserInteraction.objects.create(
                user_id=user_id,
                club_id=club_id,
                interaction_type=action,
                content=f"Recommendation feedback: {action}",
                rating=rating
            )

            # Update user profile cache
            cache_key = f"user_profile_{user_id}"
            cache.delete(cache_key)

            # Update recommendation models (asynchronous)
            asyncio.create_task(self._update_recommendation_models(user_id))

            return True

        except Exception as e:
            logger.error(f"❌ Error updating recommendation feedback: {e}")
            return False

    async def _update_recommendation_models(self, user_id: int):
        """Update recommendation models with new data"""
        try:
            # This would update the ML models with new interaction data
            # In production, you might want to retrain models periodically
            logger.info(f"🔄 Updating recommendation models for user {user_id}")

        except Exception as e:
            logger.error(f"❌ Error updating recommendation models: {e}")

    def get_recommendation_explanation(self, recommendation: Dict[str, Any],
                                     user_profile: Dict[str, Any]) -> str:
        """Generate explanation for recommendation"""
        club_id = recommendation['club_id']
        rec_type = recommendation['type']
        score = recommendation['score']

        try:
            from clubs.models import Club
            club = Club.objects.get(id=club_id)

            explanations = {
                'content': f"Рекомендовано на основе схожести с вашими интересами: {', '.join(user_profile.get('interests', [])[:2])}",
                'collaborative': "Рекомендовано потому что пользователям с похожими интересами понравилось",
                'demographic': "Популярно среди пользователей вашей демографической группы",
                'contextual': recommendation.get('reason', 'Подходит под текущий контекст'),
                'fallback': "Недавно созданный клуб, который может вас заинтересовать"
            }

            base_explanation = explanations.get(rec_type, "Рекомендовано на основе анализа вашей активности")

            # Add club-specific details
            club_details = f"{club.name} - {club.description[:100]}"
            if len(club.description) > 100:
                club_details += "..."

            return f"{base_explanation}. {club_details}"

        except Exception as e:
            logger.error(f"❌ Error generating explanation: {e}")
            return recommendation.get('reason', 'Рекомендовано системой')

    async def get_real_time_recommendations(self, user_id: int, current_context: Dict[str, Any],
                                          n_recommendations: int = 3) -> List[Dict[str, Any]]:
        """Get real-time recommendations based on current context"""
        try:
            # Get immediate contextual recommendations
            contextual_recs = await self._get_contextual_recommendations(
                {'user_id': user_id}, current_context
            )

            # Get quick content-based recommendations
            user_profile = await self._get_user_profile(user_id)
            content_recs = await self._get_content_recommendations(user_profile, current_context)

            # Combine with emphasis on contextual
            all_recs = contextual_recs[:2] + content_recs[:1]

            # Sort by score
            sorted_recs = sorted(all_recs, key=lambda x: x['score'], reverse=True)

            return sorted_recs[:n_recommendations]

        except Exception as e:
            logger.error(f"❌ Error in real-time recommendations: {e}")
            return await self._get_fallback_recommendations(current_context, n_recommendations)


# Global instance
recommendation_engine = None


def get_recommendation_engine():
    """Get recommendation engine instance"""
    global recommendation_engine
    if recommendation_engine is None:
        recommendation_engine = RecommendationEngine()
    return recommendation_engine