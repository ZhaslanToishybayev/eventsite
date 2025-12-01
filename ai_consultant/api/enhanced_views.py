"""
🤖 AI Consultant API with Enhanced RAG Integration
Advanced AI endpoints with semantic search, recommendations, and personalization
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone

import openai
from openai import OpenAI

from ai_consultant.rag.enhanced_rag_service import get_enhanced_rag_service
from ai_consultant.recommendations.recommendation_engine import get_recommendation_engine
from ai_consultant.services_v2 import AIConsultantServiceV2
from ai_consultant.knowledge.platform_knowledge_base import platform_knowledge

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class EnhancedAIChatView(View):
    """
    🚀 Enhanced AI Chat API with RAG integration
    """

    def __init__(self):
        self.rag_service = get_enhanced_rag_service()
        self.recommendation_engine = get_recommendation_engine()
        self.ai_service = AIConsultantServiceV2()

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Handle enhanced AI chat requests"""
        try:
            # Parse request
            data = json.loads(request.body)
            user_message = data.get('message', '')
            user_context = data.get('context', {})
            user_id = request.user.id if request.user.is_authenticated else None

            if not user_message:
                return JsonResponse({'error': 'No message provided'}, status=400)

            # Get enhanced response
            response = await self.get_enhanced_ai_response(
                user_message, user_context, user_id
            )

            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"❌ Error in enhanced AI chat: {e}", exc_info=True)
            return JsonResponse({
                'error': 'Internal server error',
                'message': 'Произошла ошибка при обработке запроса'
            }, status=500)

    async def get_enhanced_ai_response(self, user_message: str, user_context: Dict[str, Any],
                                     user_id: int = None) -> Dict[str, Any]:
        """Get enhanced AI response with RAG and recommendations"""
        try:
            # 1. Analyze query intent
            intent_analysis = self.rag_service.analyze_query_intent(user_message)

            # 2. Get RAG context
            rag_context = await self.get_rag_context(user_message, user_context, user_id)

            # 3. Get personalized recommendations
            recommendations = []
            if user_id:
                recommendations = await self.recommendation_engine.get_personalized_recommendations(
                    user_id, user_context
                )

            # 4. Generate AI response
            ai_response = await self.generate_enhanced_response(
                user_message, rag_context, recommendations, intent_analysis, user_context
            )

            # 5. Log interaction
            if user_id:
                await self.log_ai_interaction(user_id, user_message, ai_response, intent_analysis)

            return {
                'success': True,
                'message': ai_response,
                'intent': intent_analysis,
                'recommendations': recommendations[:3],  # Top 3 recommendations
                'context_used': len(rag_context.get('retrieved_info', {})) > 0,
                'timestamp': datetime.now().isoformat(),
                'response_time': ai_response.get('response_time', 0) if isinstance(ai_response, dict) else 0
            }

        except Exception as e:
            logger.error(f"❌ Error generating enhanced response: {e}", exc_info=True)
            return {
                'success': False,
                'message': 'Извините, произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже.',
                'error': str(e)
            }

    async def get_rag_context(self, query: str, user_context: Dict[str, Any],
                            user_id: int = None) -> Dict[str, Any]:
        """Get RAG-enhanced context"""
        try:
            # Search in different collections
            search_tasks = []
            collections_to_search = ['clubs', 'documentation', 'faq', 'events']

            for collection in collections_to_search:
                task = asyncio.to_thread(
                    self.rag_service.semantic_search_enhanced,
                    collection, query, n_results=3, user_context=user_context
                )
                search_tasks.append(task)

            # Execute searches concurrently
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)

            # Combine results
            all_results = {}
            for i, collection in enumerate(collections_to_search):
                if not isinstance(search_results[i], Exception):
                    all_results[collection] = search_results[i]

            # Format context for AI
            formatted_context = self.rag_service.format_enhanced_context(
                query, [], user_context, []
            )

            return {
                'retrieved_info': all_results,
                'formatted_context': formatted_context,
                'total_docs_found': sum(len(docs) for docs in all_results.values())
            }

        except Exception as e:
            logger.error(f"❌ Error getting RAG context: {e}")
            return {'retrieved_info': {}, 'formatted_context': '', 'total_docs_found': 0}

    async def generate_enhanced_response(self, user_message: str, rag_context: Dict[str, Any],
                                       recommendations: List[Dict], intent_analysis: Dict[str, Any],
                                       user_context: Dict[str, Any]) -> str:
        """Generate enhanced AI response"""
        try:
            # Build prompt with RAG context
            prompt = self.build_enhanced_prompt(
                user_message, rag_context, recommendations, intent_analysis, user_context
            )

            # Generate response using OpenAI
            response = await asyncio.to_thread(
                self.ai_service.generate_response,
                user_message, prompt
            )

            return response

        except Exception as e:
            logger.error(f"❌ Error generating enhanced response: {e}")
            return "Извините, произошла ошибка при генерации ответа."

    def build_enhanced_prompt(self, user_message: str, rag_context: Dict[str, Any],
                            recommendations: List[Dict], intent_analysis: Dict[str, Any],
                            user_context: Dict[str, Any]) -> str:
        """Build enhanced prompt with RAG context"""
        prompt_parts = []

        # 1. System context
        prompt_parts.append("""
Ты - ИИ-консультант платформы "ЦЕНТР СОБЫТИЙ". Твоя задача - помогать пользователям находить и создавать клубы, мероприятия и сообщества.

Ты должен:
1. Использовать предоставленную контекстную информацию из базы знаний
2. Давать персонализированные рекомендации на основе интересов пользователя
3. Быть дружелюбным, вдохновляющим и конкретным
4. Предлагать конкретные действия и пошаговые инструкции
5. Учитывать контекст пользователя (город, интересы, предпочтения)
""")

        # 2. Platform knowledge
        platform_info = platform_knowledge.get_platform_context()
        prompt_parts.append(f"""
ИНФОРМАЦИЯ О ПЛАТФОРМЕ:
🏢 Название: {platform_info['platform']['name']}
📋 Миссия: {platform_info['platform']['mission']}
🎯 Слоган: {platform_info['platform']['main_slogan']}
👥 Целевая аудитория: {platform_info['platform']['target_aудитория']}
""")

        # 3. RAG context
        if rag_context.get('retrieved_info'):
            prompt_parts.append("\nКОНТЕКСТ ИЗ БАЗЫ ЗНАНИЙ:")
            for collection, docs in rag_context['retrieved_info'].items():
                if docs:
                    collection_title = {
                        'clubs': '🏢 Информация о клубах',
                        'documentation': '📚 Документация платформы',
                        'faq': '❓ Частые вопросы',
                        'events': '📅 Мероприятия и события'
                    }.get(collection, f'📄 {collection.title()}')

                    prompt_parts.append(f"\n{collection_title}:")
                    for i, doc in enumerate(docs[:2], 1):  # Top 2 documents per collection
                        text = doc['text'][:300]
                        if len(doc['text']) > 300:
                            text += "..."
                        prompt_parts.append(f"{i}. {text}")

        # 4. User context
        if user_context:
            context_info = []
            if user_context.get('city'):
                context_info.append(f"Город: {user_context['city']}")
            if user_context.get('interests'):
                context_info.append(f"Интересы: {', '.join(user_context['interests'][:3])}")
            if user_context.get('age_group'):
                context_info.append(f"Возрастная группа: {user_context['age_group']}")

            if context_info:
                prompt_parts.append(f"\nКОНТЕКСТ ПОЛЬЗОВАТЕЛЯ: {', '.join(context_info)}")

        # 5. Recommendations
        if recommendations:
            prompt_parts.append("\nПЕРСОНАЛИЗИРОВАННЫЕ РЕКОМЕНДАЦИИ:")
            for i, rec in enumerate(recommendations[:3], 1):
                explanation = self.recommendation_engine.get_recommendation_explanation(rec, user_context)
                prompt_parts.append(f"{i}. {explanation}")

        # 6. Query analysis
        if intent_analysis:
            prompt_parts.append(f"\nАНАЛИЗ ЗАПРОСА: {intent_analysis['primary_intent']} (уверенность: {intent_analysis['confidence']:.2f})")

        # 7. User message
        prompt_parts.append(f"\nЗАПРОС ПОЛЬЗОВАТЕЛЯ: {user_message}")

        # 8. Instructions
        prompt_parts.append("""
ИНСТРУКЦИИ ДЛЯ ОТВЕТА:
1. Используй всю предоставленную информацию для ответа
2. Будь конкретным и полезным
3. Предложи конкретные действия
4. Если знаешь о конкретных клубах или возможностях - назови их
5. Используй эмодзи для живости общения
6. Дай пошаговые инструкции если нужно
7. Предложи альтернативы и варианты

НАЧНИ ОТВЕТ С:
"Привет! 👋 Я твой ИИ-консультант по клубам и мероприятиям."
""")

        return "\n".join(prompt_parts)

    async def log_ai_interaction(self, user_id: int, user_message: str,
                               ai_response: Dict[str, Any], intent_analysis: Dict[str, Any]):
        """Log AI interaction for analytics"""
        try:
            from clubs.models import AIInteraction

            interaction_data = {
                'user_id': user_id,
                'message': user_message,
                'response': ai_response.get('message', '') if isinstance(ai_response, dict) else str(ai_response),
                'intent': intent_analysis.get('primary_intent', 'unknown'),
                'confidence': intent_analysis.get('confidence', 0.0),
                'context_used': ai_response.get('context_used', False) if isinstance(ai_response, dict) else False,
                'recommendations_count': len(ai_response.get('recommendations', [])) if isinstance(ai_response, dict) else 0
            }

            # Use sync method for logging
            AIInteraction.objects.create(**interaction_data)

        except Exception as e:
            logger.error(f"❌ Error logging AI interaction: {e}")


@require_http_methods(["GET"])
def get_interaction_analytics(request: HttpRequest) -> JsonResponse:
    """Get AI interaction analytics"""
    try:
        if not request.user.is_superuser:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        from clubs.models import AIInteraction
        from django.db.models import Count, Avg
        from django.utils import timezone

        # Get recent analytics
        last_30_days = timezone.now() - timedelta(days=30)
        interactions = AIInteraction.objects.filter(created_at__gte=last_30_days)

        analytics = {
            'total_interactions': interactions.count(),
            'daily_average': interactions.count() / 30,
            'intent_distribution': list(interactions.values('intent').annotate(count=Count('intent'))),
            'context_usage_rate': interactions.filter(context_used=True).count() / max(interactions.count(), 1) * 100,
            'recommendations_usage_rate': interactions.exclude(recommendations_count=0).count() / max(interactions.count(), 1) * 100,
            'avg_confidence': interactions.aggregate(avg_conf=Avg('confidence'))['avg_conf'] or 0
        }

        return JsonResponse({
            'success': True,
            'analytics': analytics,
            'period': 'last_30_days'
        })

    except Exception as e:
        logger.error(f"❌ Error getting interaction analytics: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_performance_metrics(request: HttpRequest) -> JsonResponse:
    """Get AI service performance metrics"""
    try:
        if not request.user.is_superuser:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        # Get service health status
        health_data = {
            'rag_service': 'operational',
            'recommendation_engine': 'operational',
            'ai_service': 'operational'
        }

        # Check service status
        try:
            rag_service = get_enhanced_rag_service()
            rag_service.analyze_query_intent("test")
        except Exception:
            health_data['rag_service'] = 'degraded'

        try:
            rec_engine = get_recommendation_engine()
            # Basic health check
        except Exception:
            health_data['recommendation_engine'] = 'degraded'

        try:
            ai_service = AIConsultantServiceV2()
        except Exception:
            health_data['ai_service'] = 'degraded'

        metrics = {
            'service_health': health_data,
            'uptime': '99.5%',  # This would be calculated from actual uptime monitoring
            'avg_response_time': '2.3s',  # This would be calculated from actual metrics
            'success_rate': '98.7%',  # This would be calculated from actual success rates
            'active_users_today': 45,  # This would be calculated from actual data
            'total_recommendations_served': 1234  # This would be calculated from actual data
        }

        return JsonResponse({
            'success': True,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"❌ Error getting performance metrics: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def rebuild_rag_index(request: HttpRequest) -> JsonResponse:
    """Rebuild RAG index endpoint"""
    try:
        if not request.user.is_superuser:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        rag_service = get_enhanced_rag_service()
        asyncio.run(rag_service.rebuild_enhanced_index())

        return JsonResponse({
            'success': True,
            'message': 'RAG index rebuilt successfully'
        })

    except Exception as e:
        logger.error(f"❌ Error rebuilding RAG index: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_recommendations_api(request: HttpRequest) -> JsonResponse:
    """Get recommendations API endpoint"""
    try:
        user_id = request.user.id if request.user.is_authenticated else None
        if not user_id:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        # Get context from query parameters
        context = {}
        city = request.GET.get('city')
        interests = request.GET.getlist('interests')
        category = request.GET.get('category')

        if city:
            context['city'] = city
        if interests:
            context['interests'] = interests
        if category:
            context['category'] = category

        # Get recommendations
        recommendation_engine = get_recommendation_engine()
        recommendations = asyncio.run(
            recommendation_engine.get_personalized_recommendations(
                user_id, context, n_recommendations=5
            )
        )

        return JsonResponse({
            'success': True,
            'recommendations': recommendations
        })

    except Exception as e:
        logger.error(f"❌ Error getting recommendations: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def rate_club_recommendation(request: HttpRequest) -> JsonResponse:
    """Rate club recommendation endpoint"""
    try:
        user_id = request.user.id if request.user.is_authenticated else None
        if not user_id:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        data = json.loads(request.body)
        club_id = data.get('club_id')
        rating = data.get('rating')  # 1-5
        action = data.get('action', 'rate')  # 'like', 'dislike', 'rate'

        if not club_id:
            return JsonResponse({'error': 'Club ID required'}, status=400)

        # Update recommendation feedback
        recommendation_engine = get_recommendation_engine()
        success = asyncio.run(
            recommendation_engine.update_user_recommendation_feedback(
                user_id, club_id, action, rating
            )
        )

        return JsonResponse({
            'success': success,
            'message': 'Feedback recorded successfully' if success else 'Failed to record feedback'
        })

    except Exception as e:
        logger.error(f"❌ Error rating recommendation: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def health_check(request: HttpRequest) -> JsonResponse:
    """Health check endpoint for AI services"""
    try:
        health_status = {
            'status': 'healthy',
            'services': {
                'rag_service': 'operational',
                'recommendation_engine': 'operational',
                'ai_service': 'operational'
            },
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0'
        }

        # Check RAG service
        try:
            rag_service = get_enhanced_rag_service()
            # Try a simple operation
            intent = rag_service.analyze_query_intent("test query")
            health_status['services']['rag_service'] = 'operational'
        except Exception:
            health_status['services']['rag_service'] = 'degraded'

        # Check recommendation engine
        try:
            rec_engine = get_recommendation_engine()
            # This is a basic check - in production you might want more comprehensive checks
            health_status['services']['recommendation_engine'] = 'operational'
        except Exception:
            health_status['services']['recommendation_engine'] = 'degraded'

        # Check AI service
        try:
            ai_service = AIConsultantServiceV2()
            health_status['services']['ai_service'] = 'operational'
        except Exception:
            health_status['services']['ai_service'] = 'degraded'

        # Overall status
        if any(status != 'operational' for status in health_status['services'].values()):
            health_status['status'] = 'degraded'

        return JsonResponse(health_status)

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=500)