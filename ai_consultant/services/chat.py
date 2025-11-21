"""
💬 Чат сервис v2.0
Управление сессиями и сообщениями
"""

import logging
import json
from typing import Dict, Any, List, Optional
from django.contrib.auth import get_user_model
from django.db import transaction, models
from django.utils import timezone
from django.core.cache import cache

from ..models import ChatSession, ChatMessage, ConversationState
from .base import BaseAIService
from .cache_manager import ResponseCacheManager
from ..metrics.collector import MetricsCollector
from .context_builder import ContextBuilder
from .language import LanguageService
from ..agents.tools import ToolExecutor

# Agents
from ..agents.router import AgentRouter
from ..agents.registry import AgentRegistry
# Import specialists to ensure registration
from ..agents.specialists import *

User = get_user_model()
logger = logging.getLogger(__name__)


class ChatService(BaseAIService):
    """
    Сервис для управления чат-сессиями и сообщениями
    """

    def __init__(self, openai_service, service_provider=None):
        super().__init__()
        self.openai_service = openai_service
        self.service_provider = service_provider
        self.max_history_length = 50  # Максимальная длина истории
        self.cache_manager = ResponseCacheManager()
        self.metrics = MetricsCollector()
        self.context_builder = ContextBuilder()
        self.language_service = LanguageService()
        
        # Initialize Router
        self.router = AgentRouter(openai_service)
        
        # Initialize Tool Executor
        self.tool_executor = ToolExecutor(service_provider) if service_provider else None

    def process(self, session: ChatSession, message: str, **kwargs) -> Dict[str, Any]:
        """
        Основной метод обработки сообщения
        """
        return self.send_message(session, message, **kwargs)

    def create_session(self, user: User) -> ChatSession:
        """
        Создает новую чат-сессию
        """
        try:
            with transaction.atomic():
                session = ChatSession.objects.create(
                    user=user,
                    is_active=True
                )

                self.log_info(f"Создана новая сессия", {
                    'session_id': session.id,
                    'user_id': user.id
                })
                
                self.metrics.record_request(request_type='create_session')
                return session
        except Exception as e:
            self.log_error(f"Ошибка создания сессии: {e}")
            self.metrics.record_error('create_session_error')
            raise

    def send_message(self, session: ChatSession, message: str, context_service=None, enhanced_context=None) -> Dict[str, Any]:
        """
        Отправляет сообщение и получает ответ от ИИ
        """
        import time
        start_time = time.time()
        
        try:
            with transaction.atomic():
                # 1. Сохраняем сообщение пользователя
                user_message = self._save_message(session, message, is_from_user=True)

                # 2. Определяем историю сообщений для роутинга
                history = self.get_history(session, limit=5)
                
                # 3. Роутинг: выбираем агента (с сохранением контекста)
                # Проверяем есть ли уже активный агент в сессии
                if session.current_agent:
                    # Продолжаем с текущим агентом
                    agent_name = session.current_agent
                    logger.info(f"📌 Продолжаем с агентом: {agent_name}")
                    
                    # Проверяем нужно ли сбросить агента (смена темы)
                    should_reset = self._should_reset_agent(message, history, session)
                    if should_reset:
                        logger.info(f"🔄 Сброс агента из-за смены темы")
                        agent_name = self.router.route(message, history)
                        session.current_agent = agent_name
                        session.agent_context = {}
                        session.save(update_fields=['current_agent', 'agent_context'])
                        logger.info(f"🆕 Новый агент после сброса: {agent_name}")
                else:
                    # Роутим только если нет активного агента
                    agent_name = self.router.route(message, history)
                    session.current_agent = agent_name
                    session.save(update_fields=['current_agent'])
                    logger.info(f"🆕 Новый агент: {agent_name}")
                
                agent_class = AgentRegistry.get_agent(agent_name)
                
                if not agent_class:
                    raise ValueError(f"Agent {agent_name} not found in registry")
                
                agent = agent_class(context_service) # Pass context_service to agent constructor
                
                # 4. TEMPORARILY DISABLED: Let new agent system handle club creation directly
                # if agent_name == 'club_specialist':
                #     intercepted = self._handle_club_creation_flow(session, message)
                #     if intercepted:
                #         # intercepted is a ready response dict
                #         return intercepted
                
                # 5. Строим контекст для OpenAI
                messages_context = self._build_messages_context(session, message, agent, context_service)
                
                # 6. Вызываем OpenAI с инструментами агента
                tools = agent.get_tools() if agent else []
                
                logger.info(f"📤 Sending to OpenAI: agent={agent_name}, tools_count={len(tools)}")
                if tools:
                    logger.info(f"🔧 Available tools: {[t['function']['name'] for t in tools]}")
                
                # Log the last user message for debugging
                user_messages = [m for m in messages_context if m.get('role') == 'user']
                if user_messages:
                    logger.info(f"📝 User message: {user_messages[-1].get('content', '')[:100]}...")
                
                # 🎉 UPGRADED TO GPT-4O-MINI - Tools now working!
                tools = agent.get_tools() if agent else []

                logger.info(f"📤 Sending to OpenAI: agent={agent_name}, tools_count={len(tools)}, model=gpt-4o-mini")

                # Use auto tool choice - let the model decide
                tool_choice = "auto" if tools else None
                
                try:
                    ai_response = self.openai_service.chat_completion(
                        messages=messages_context,
                        tools=tools,
                        tool_choice=tool_choice
                    )
                except Exception as e:
                    logger.error(f"❌ OpenAI API call failed: {e}")
                    # Return a helpful fallback response
                    fallback_response = self._get_fallback_response_for_agent(agent_name, message)
                    ai_message = self._save_message(session, fallback_response, is_from_user=False)
                    return {
                        'response': fallback_response,
                        'session_id': session.id,
                        'message_id': ai_message.id,
                        'tokens_used': 0
                    }
                
                # Check if response is valid
                if not ai_response.get('success'):
                    logger.error(f"❌ OpenAI returned error: {ai_response.get('error')}")
                    fallback_response = self._get_fallback_response_for_agent(agent_name, message)
                    ai_message = self._save_message(session, fallback_response, is_from_user=False)
                    return {
                        'response': fallback_response,
                        'session_id': session.id,
                        'message_id': ai_message.id,
                        'tokens_used': 0
                    }
                
                content = ai_response.get('content', '').strip()
                tool_calls = ai_response.get('tool_calls')
                
                logger.info(f"📥 OpenAI response: content_length={len(content)}, has_tool_calls={bool(tool_calls)}")
                
                # If both content and tool_calls are empty, use fallback
                if not content and not tool_calls:
                    logger.error(f"❌ Empty response from OpenAI - both content and tool_calls are empty")
                    fallback_response = self._get_fallback_response_for_agent(agent_name, message)
                    ai_message = self._save_message(session, fallback_response, is_from_user=False)
                    return {
                        'response': fallback_response,
                        'session_id': session.id,
                        'message_id': ai_message.id,
                        'tokens_used': 0
                    }

                
                if tool_calls:
                    # Append assistant message with tool calls
                    messages_context.append({
                        "role": "assistant",
                        "content": ai_response.get('content') or "",
                        "tool_calls": tool_calls
                    })
                    
                    # Execute each tool
                    for tool_call in tool_calls:
                        tool_call_id = tool_call.get('id')
                        func_name = tool_call.get('function', {}).get('name')
                        func_args_str = tool_call.get('function', {}).get('arguments', '{}')
                        
                        try:
                            # Очистка строки от невалидных символов
                            func_args_str = func_args_str.strip()
                            if not func_args_str:
                                func_args_str = '{}'
                            func_args = json.loads(func_args_str)
                        except json.JSONDecodeError as e:
                            logger.error(f"❌ JSON parse error in tool arguments: {e}")
                            logger.error(f"   Raw arguments: {repr(func_args_str)}")
                            func_args = {}

                            
                        # Execute tool
                        logger.info(f"🔧 Executing tool: {func_name} with args: {func_args}")
                        tool_result = self.tool_executor.execute(agent_name, func_name, func_args, session.user)
                        logger.info(f"✅ Tool result: {tool_result[:200]}...")
                        
                        # Append tool result
                        messages_context.append({
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": tool_result
                        })
                    
                    # Call OpenAI again with tool results
                    logger.info(f"🔄 Calling OpenAI again with {len(messages_context)} messages")
                    second_response = self.openai_service.chat_completion(
                        messages=messages_context,
                        tools=tools if tools else None, # Tools might still be relevant for subsequent calls
                        tool_choice="auto" if tools else None
                    )
                    logger.info(f"✅ Second response: {second_response.get('content', '')[:200]}...")
                    ai_response['tokens_used'] += second_response.get('tokens_used', 0)
                    ai_response['content'] = second_response.get('content', '')

                
                response_content = ai_response.get('content', 'Извините, я не смог сформировать ответ.')
                
                # 7.5. Проверяем нужно ли сбросить агента (завершение процесса)
                if self._is_process_completed(response_content, agent_name):
                    logger.info(f"✅ Процесс завершен, сбрасываем агента")
                    session.current_agent = None
                    session.agent_context = {}
                    session.save(update_fields=['current_agent', 'agent_context'])
                
                # 8. Сохраняем ответ ИИ
                ai_message = self._save_message(
                    session,
                    response_content,
                    is_from_user=False,
                    tokens_used=ai_response.get('tokens_used', 0)
                )
            
            duration = time.time() - start_time
            self.metrics.record_response_time(duration)
            self.metrics.record_tokens(ai_response.get('tokens_used', 0))

            return {
                'response': response_content,
                'message_id': ai_message.id,
                'tokens_used': ai_response.get('tokens_used', 0),
                'session_id': session.id,
                'agent': agent_name
            }

        except Exception as e:
            self.metrics.record_error('chat_error')
            self.metrics.record_request(status='error')
            self.log_error(f"Ошибка отправки сообщения: {e}")
            raise

    def get_history(self, session: ChatSession, limit: int = None) -> List[Dict[str, Any]]:
        """
        Получает историю сообщений сессии
        """
        try:
            limit = limit or self.max_history_length

            messages = ChatMessage.objects.filter(
                session=session
            ).order_by('created_at')[:limit]

            history = []
            for message in messages:
                history.append({
                    'id': message.id,
                    'content': message.content,
                    'is_from_user': message.role == 'user',
                    'created_at': message.created_at.isoformat(),
                    'tokens_used': message.tokens_used or 0
                })
            return history
        except Exception as e:
            self.log_error(f"Ошибка получения истории: {e}")
            return []

    def get_messages_count(self, session: ChatSession) -> int:
        """
        Получает общее количество сообщений в сессии

        Args:
            session: Сессия чата

        Returns:
            int: Количество сообщений
        """
        try:
            return ChatMessage.objects.filter(session=session).count()
        except Exception as e:
            self.log_error(f"Ошибка получения количества сообщений: {e}")
            return 0

    def delete_session(self, session: ChatSession) -> bool:
        """
        Удаляет сессию и все связанные сообщения
        """
        try:
            with transaction.atomic():
                session.messages.all().delete()
                session.delete()
                self._clear_history_cache(session.id)
                return True
        except Exception as e:
            self.log_error(f"Ошибка удаления сессии: {e}")
            return False

    def get_session_stats(self, session: ChatSession) -> Dict[str, Any]:
        """
        Получает статистику сессии
        """
        try:
            messages = ChatMessage.objects.filter(session=session)
            total_tokens = messages.aggregate(total=models.Sum('tokens_used'))['total'] or 0
            
            return {
                'session_id': session.id,
                'total_messages': messages.count(),
                'total_tokens_used': total_tokens
            }
        except Exception as e:
            self.log_error(f"Ошибка получения статистики: {e}")
            return {}

    def get_user_sessions(self, user: User, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Получает сессии пользователя
        """
        try:
            sessions = ChatSession.objects.filter(user=user, is_active=True).order_by('-updated_at')[:limit]
            return [{'id': s.id, 'created_at': s.created_at} for s in sessions]
        except Exception as e:
            self.log_error(f"Ошибка получения сессий: {e}")
            return []

    def get_user_analytics(self, user: User) -> Dict[str, Any]:
        """
        Получает аналитику пользователя
        """
        # Simplified for brevity
        return {'user_id': user.id}

    # Вспомогательные методы

    def _save_message(self, session: ChatSession, content: str, is_from_user: bool, tokens_used: int = 0) -> ChatMessage:
        role = 'user' if is_from_user else 'assistant'
        return ChatMessage.objects.create(
            session=session,
            content=content,
            role=role,
            tokens_used=tokens_used
        )

    def _build_messages_context(self, session: ChatSession, current_message: str, agent, context_service=None) -> List[Dict[str, str]]:
        """
        Строит контекст для OpenAI из истории сообщений
        """
        messages = []

        # 1. System Prompt from Agent
        system_prompt = agent.get_system_prompt()
        messages.append({"role": "system", "content": system_prompt})

        # 2. History
        history = self.get_history(session, limit=self.max_history_length - 2)
        for msg in history:
            role = "user" if msg['is_from_user'] else "assistant"
            messages.append({
                "role": role,
                "content": msg['content']
            })

        # 3. Current Message
        messages.append({"role": "user", "content": current_message})

        return self.openai_service.truncate_messages(messages)

    def _clear_history_cache(self, session_id: str):
        try:
            cache.delete_many([f"chat_history_{session_id}_*"])
        except Exception as e:
            self.log_error(f"Ошибка очистки кэша: {e}")
    
    def _get_fallback_response_for_agent(self, agent_name: str, user_message: str) -> str:
        """
        Returns a helpful fallback response based on agent type
        """
        responses = {
            'club_specialist': "Я могу помочь вам найти клубы и сообщества! Попробуйте спросить:\n- 'Какие есть клубы по футболу?'\n- 'Покажи спортивные сообщества'\n- 'Хочу найти клуб по программированию'",
            'support_specialist': "Я помогу вам разобраться с платформой! Вот что я могу:\n- Помочь с регистрацией и входом\n- Объяснить, как создать клуб\n- Ответить на вопросы о функциях платформы",
            'mentor_specialist': "Я могу помочь с вашим развитием! Спросите меня:\n- 'Какие курсы доступны?'\n- 'Хочу научиться программированию'\n- 'Покажи мой прогресс'",
            'orchestrator': "Привет! 👋 Я AI-консультант платформы ЦЕНТР СОБЫТИЙ.\n\nЯ могу помочь вам:\n🔍 Найти интересные клубы и сообщества\n📚 Узнать о функциях платформы\n🎯 Развивать свои навыки\n\nЧем могу помочь?"
        }
        
        return responses.get(agent_name, "Привет! Чем могу помочь? 🌟")

    def health_check(self) -> bool:
        try:
            ChatSession.objects.count()
            return True
        except Exception:
            return False

    # ====== Club Creation State Machine ======
    def _detect_create_intent(self, text: str) -> bool:
        t = (text or '').lower()
        keywords = [
            'создать', 'создай', 'хочу создать', 'не ищу, хочу создать', 'не ищу клуб, хочу создать',
            'создать клуб', 'создать сообщество'
        ]
        return any(k in t for k in keywords)

    def _get_or_create_state(self, session: ChatSession) -> ConversationState:
        state, created = ConversationState.objects.get_or_create(
            session_id=str(session.id),
            defaults={'stage': 'welcome', 'data': {}}
        )
        return state

    def _handle_club_creation_flow(self, session: ChatSession, user_message: str) -> Optional[Dict[str, Any]]:
        """
        Returns a ready response dict if the club creation flow consumed the message,
        otherwise returns None to continue with LLM.
        """
        state = self._get_or_create_state(session)
        msg = (user_message or '').strip()

        # If intent detected and stage is welcome/done, move to name step
        if self._detect_create_intent(msg) and state.stage in ['welcome', 'done']:
            state.stage = 'name'
            state.update_progress()
            state.save(update_fields=['stage', 'updated_at', 'progress'])
            response = "Отлично! Давай создадим твой клуб!\n\nШаг 1: Как назовем клуб? Придумай уникальное имя (минимум 3 символа)."
            ai_message = self._save_message(session, response, is_from_user=False)
            return {
                'response': response,
                'session_id': session.id,
                'message_id': ai_message.id,
                'tokens_used': 0,
                'agent': 'club_specialist'
            }

        # Stage machine
        if state.stage == 'name':
            if len(msg) < 3:
                response = "Название слишком короткое. Укажи, пожалуйста, название минимум из 3 символов."
            else:
                data = state.data or {}
                data['name'] = msg
                state.data = data
                state.stage = 'description'
                state.update_progress()
                state.save(update_fields=['data', 'stage', 'updated_at', 'progress'])
                response = (
                    "Отлично!\n\nШаг 2: Расскажи подробнее об идее клуба (минимум 200 символов):\n"
                    "• Кто целевая аудитория?\n"
                    "• Какие активности/мероприятия планируете?\n"
                    "• В чем уникальность клуба?\n"
                )
            ai_message = self._save_message(session, response, is_from_user=False)
            return {
                'response': response,
                'session_id': session.id,
                'message_id': ai_message.id,
                'tokens_used': 0,
                'agent': 'club_specialist'
            }

        if state.stage == 'description':
            if len(msg) < 200:
                response = "Описание пока коротковато. Нужно минимум 200 символов, добавь деталей, пожалуйста."
                ai_message = self._save_message(session, response, is_from_user=False)
                return {
                    'response': response,
                    'session_id': session.id,
                    'message_id': ai_message.id,
                    'tokens_used': 0,
                    'agent': 'club_specialist'
                }
            data = state.data or {}
            data['description'] = msg
            state.data = data
            state.stage = 'category'
            state.update_progress()
            state.save(update_fields=['data', 'stage', 'updated_at', 'progress'])
            response = (
                "Шаг 3: Выбери категорию клуба:\nСпорт / Хобби / IT / Профессия / Творчество / Образование / Бизнес"
            )
            ai_message = self._save_message(session, response, is_from_user=False)
            return {
                'response': response,
                'session_id': session.id,
                'message_id': ai_message.id,
                'tokens_used': 0,
                'agent': 'club_specialist'
            }

        if state.stage == 'category':
            data = state.data or {}
            data['category'] = msg
            state.data = data
            state.stage = 'city'
            state.update_progress()
            state.save(update_fields=['data', 'stage', 'updated_at', 'progress'])
            response = "Шаг 4: В каком городе будет клуб? (можно пропустить, напиши 'без города')"
            ai_message = self._save_message(session, response, is_from_user=False)
            return {
                'response': response,
                'session_id': session.id,
                'message_id': ai_message.id,
                'tokens_used': 0,
                'agent': 'club_specialist'
            }

        if state.stage == 'city':
            data = state.data or {}
            if msg.lower() not in ['без города', 'нет', 'пропустить']:
                data['city'] = msg
            state.data = data
            state.stage = 'confirm'
            state.update_progress()
            state.save(update_fields=['data', 'stage', 'updated_at', 'progress'])
            name = data.get('name', '—')
            description = (data.get('description', '')[:200] + '...') if data.get('description') else '—'
            category = data.get('category', '—')
            city = data.get('city', '—')
            response = (
                f"Проверь данные:\n\n"
                f"Название: {name}\n"
                f"Категория: {category}\n"
                f"Город: {city}\n"
                f"Описание: {description}\n\n"
                f"Все верно? Напиши 'Да' для создания или 'Нет', если нужно исправить."
            )
            ai_message = self._save_message(session, response, is_from_user=False)
            return {
                'response': response,
                'session_id': session.id,
                'message_id': ai_message.id,
                'tokens_used': 0,
                'agent': 'club_specialist'
            }

        if state.stage == 'confirm':
            lower = msg.lower()
            if lower in ['да', 'создать', 'подтверждаю', 'ок', 'yes']:
                # Call the real create_club tool via ToolExecutor
                data = state.data or {}
                tool_args = {
                    'name': data.get('name'),
                    'description': data.get('description'),
                    'category': data.get('category'),
                    'city': data.get('city'),
                    'is_private': False
                }
                tool_output = None
                try:
                    if self.tool_executor is None:
                        raise ValueError('Tool executor is not configured')
                    tool_output = self.tool_executor.execute('club_specialist', 'create_club', tool_args, session.user)
                except Exception as e:
                    logger.error(f"❌ Failed to execute create_club tool: {e}")
                    tool_output = json.dumps({
                        'status': 'error',
                        'message': f'Не удалось создать клуб: {str(e)}'
                    }, ensure_ascii=False)
                
                # Parse tool result
                try:
                    tool_json = json.loads(tool_output) if isinstance(tool_output, str) else tool_output
                except Exception:
                    tool_json = {'status': 'error', 'message': str(tool_output)}
                
                if tool_json.get('status') == 'success':
                    # Reset state and agent
                    state.stage = 'done'
                    state.update_progress()
                    state.save(update_fields=['stage', 'updated_at', 'progress'])
                    session.current_agent = None
                    session.agent_context = {}
                    session.save(update_fields=['current_agent', 'agent_context'])
                    response = tool_json.get('message') or "Клуб успешно создан! 🎉"
                    ai_message = self._save_message(session, response, is_from_user=False)
                    return {
                        'response': response,
                        'session_id': session.id,
                        'message_id': ai_message.id,
                        'tokens_used': 0,
                        'agent': 'club_specialist',
                        'club_id': tool_json.get('club_id'),
                        'link': tool_json.get('link')
                    }
                else:
                    # Stay on confirm, show error and allow correction
                    response = tool_json.get('message', 'Не удалось создать клуб. Пожалуйста, проверьте данные и попробуйте снова.')
                    ai_message = self._save_message(session, response, is_from_user=False)
                    return {
                        'response': response,
                        'session_id': session.id,
                        'message_id': ai_message.id,
                        'tokens_used': 0,
                        'agent': 'club_specialist',
                        'errors': tool_json
                    }
            # Handle corrections
            elif any(k in lower for k in ['название', 'имя']):
                state.stage = 'name'
                state.update_progress()
                state.save(update_fields=['stage', 'updated_at', 'progress'])
                response = "Изменим название. Введите новое название клуба (минимум 3 символа)."
                ai_message = self._save_message(session, response, is_from_user=False)
                return {
                    'response': response,
                    'session_id': session.id,
                    'message_id': ai_message.id,
                    'tokens_used': 0,
                    'agent': 'club_specialist'
                }
            elif any(k in lower for k in ['описание', 'description']):
                state.stage = 'description'
                state.update_progress()
                state.save(update_fields=['stage', 'updated_at', 'progress'])
                response = "Ок, обновим описание. Напишите полное описание (минимум 200 символов)."
                ai_message = self._save_message(session, response, is_from_user=False)
                return {
                    'response': response,
                    'session_id': session.id,
                    'message_id': ai_message.id,
                    'tokens_used': 0,
                    'agent': 'club_specialist'
                }
            elif any(k in lower for k in ['категор', 'category']):
                state.stage = 'category'
                state.update_progress()
                state.save(update_fields=['stage', 'updated_at', 'progress'])
                response = "Выберите новую категорию: Спорт / Хобби / IT / Профессия / Творчество / Образование / Бизнес"
                ai_message = self._save_message(session, response, is_from_user=False)
                return {
                    'response': response,
                    'session_id': session.id,
                    'message_id': ai_message.id,
                    'tokens_used': 0,
                    'agent': 'club_specialist'
                }
            elif any(k in lower for k in ['город', 'city']):
                state.stage = 'city'
                state.update_progress()
                state.save(update_fields=['stage', 'updated_at', 'progress'])
                response = "Введите новый город (или напишите 'без города')."
                ai_message = self._save_message(session, response, is_from_user=False)
                return {
                    'response': response,
                    'session_id': session.id,
                    'message_id': ai_message.id,
                    'tokens_used': 0,
                    'agent': 'club_specialist'
                }
            elif lower in ['нет', 'no', 'не', 'исправить', 'поменять']:
                response = "Что нужно исправить? Название, описание, категорию или город?"
                ai_message = self._save_message(session, response, is_from_user=False)
                return {
                    'response': response,
                    'session_id': session.id,
                    'message_id': ai_message.id,
                    'tokens_used': 0,
                    'agent': 'club_specialist'
                }
            else:
                # If no, ask what to change, but keep it simple for now
                response = "Я понял, что требуется уточнение. Что нужно исправить? Название, описание, категорию или город?"
                ai_message = self._save_message(session, response, is_from_user=False)
                return {
                    'response': response,
                    'session_id': session.id,
                    'message_id': ai_message.id,
                    'tokens_used': 0,
                    'agent': 'club_specialist'
                }

        return None
    
    def _should_reset_agent(self, message: str, history: List[Dict], session) -> bool:
        """
        Определяет нужно ли сбросить текущего агента и выбрать нового
        
        Сбрасываем агента если:
        - Пользователь явно меняет тему
        - Прошло много сообщений без прогресса (10+)
        - Пользователь говорит "хватит", "стоп", "другая тема" и т.п.
        """
        message_lower = message.lower()
        
        # Ключевые слова смены темы
        topic_change_keywords = [
            'хватит', 'стоп', 'stop', 'достаточно', 'другая тема',
            'другой вопрос', 'не хочу', 'отмена', 'cancel',
            'не надо', 'нет спасибо', 'спасибо не надо'
        ]
        
        for keyword in topic_change_keywords:
            if keyword in message_lower:
                return True
        
        # Проверяем количество сообщений с текущим агентом
        agent_message_count = len([
            msg for msg in history 
            if msg.get('role') == 'user'
        ])
        
        # Если больше 15 сообщений - сбрасываем (вероятно застряли)
        if agent_message_count > 15:
            logger.warning(f"⚠️ Слишком много сообщений ({agent_message_count}), сброс агента")
            return True
        
        return False
    
    def _is_process_completed(self, response: str, agent_name: str) -> bool:
        """
        Определяет завершен ли процесс (например, создание клуба)
        
        Признаки завершения:
        - Ответ содержит "создан успешно", "поздравляю"
        - Ответ содержит ссылку на созданный объект
        - Процесс явно завершен
        """
        response_lower = response.lower()
        
        # Ключевые фразы завершения для club_specialist
        if agent_name == 'club_specialist':
            completion_keywords = [
                'клуб создан', 'успешно создан', 'поздравляю',
                'клуб опубликован', 'готово', 'создание завершено',
                'ваш клуб доступен'
            ]
            
            for keyword in completion_keywords:
                if keyword in response_lower:
                    return True
        
        return False