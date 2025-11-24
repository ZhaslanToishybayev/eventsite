"""
AI Consultant Views for UnitySphere
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import logging

from ai_agent import UnitySphereAIAgent

logger = logging.getLogger(__name__)

def ai_consultant_page(request):
    """Страница AI консультанта"""
    return render(request, 'ai_consultant/chat.html')

@csrf_exempt
def ai_chat_api(request):
    """AI Chat API endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()

            if not user_message:
                return JsonResponse({
                    'error': 'Пустое сообщение'
                }, status=400)

            # Initialize AI agent
            agent = UnitySphereAIAgent()

            # Process different types of requests
            response = process_user_request(agent, user_message)

            return JsonResponse({
                'success': True,
                'response': response,
                'message': 'AI response generated successfully'
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Некорректный JSON'
            }, status=400)
        except Exception as e:
            logger.error(f"AI Chat API error: {str(e)}")
            return JsonResponse({
                'error': 'Произошла ошибка при обработке запроса'
            }, status=500)

    return JsonResponse({
        'error': 'Метод не поддерживается'
    }, status=405)

def process_user_request(agent, message):
    """Process user request and return appropriate response"""
    message_lower = message.lower()

    # Keywords for different types of requests
    club_keywords = ['создать', 'создание', 'клуб', 'фан-клуб', 'фанатский']
    event_keywords = ['мероприяти', 'событи', 'турнир', 'встреча', 'активность']
    community_keywords = ['участник', 'активность', 'вовлеч', 'общение', 'коммуникация']

    # Check for club creation help
    if any(keyword in message_lower for keyword in club_keywords):
        return agent.get_club_creation_advice(
            club_type="любой",
            interests="различные интересы",
            goals="создание активного сообщества"
        )

    # Check for event ideas
    elif any(keyword in message_lower for keyword in event_keywords):
        return agent.get_event_ideas(
            club_type="фан-клуб",
            budget="разный",
            audience_size="разная"
        )

    # Check for community tips
    elif any(keyword in message_lower for keyword in community_keywords):
        return agent.get_community_engagement_tips(
            club_type="фан-клуб",
            member_count="разное количество"
        )

    # Default: general question
    else:
        return agent.answer_general_question(message)

@csrf_exempt
def ai_club_help_api(request):
    """AI API for club creation help"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            club_type = data.get('club_type', '')
            interests = data.get('interests', '')
            goals = data.get('goals', '')

            if not club_type or not interests:
                return JsonResponse({
                    'error': 'Требуется тип клуба и интересы'
                }, status=400)

            agent = UnitySphereAIAgent()
            advice = agent.get_club_creation_advice(club_type, interests, goals)

            return JsonResponse({
                'success': True,
                'advice': advice
            })

        except Exception as e:
            logger.error(f"AI Club Help API error: {str(e)}")
            return JsonResponse({
                'error': 'Произошла ошибка'
            }, status=500)

    return JsonResponse({
        'error': 'Метод не поддерживается'
    }, status=405)

@csrf_exempt
def ai_event_ideas_api(request):
    """AI API for event ideas"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            club_type = data.get('club_type', '')
            budget = data.get('budget', '')
            audience_size = data.get('audience_size', '')

            if not club_type:
                return JsonResponse({
                    'error': 'Требуется тип клуба'
                }, status=400)

            agent = UnitySphereAIAgent()
            ideas = agent.get_event_ideas(club_type, budget, audience_size)

            return JsonResponse({
                'success': True,
                'ideas': ideas
            })

        except Exception as e:
            logger.error(f"AI Event Ideas API error: {str(e)}")
            return JsonResponse({
                'error': 'Произошла ошибка'
            }, status=500)

    return JsonResponse({
        'error': 'Метод не поддерживается'
    }, status=405)

# Template for AI chat interface
AI_CHAT_TEMPLATE = """
{% extends 'base.html' %}

{% block title %}AI Консультант - fan-club.kz{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-md-12">
            <h1>🤖 AI Консультант</h1>
            <p class="lead">Помогу создать и развить ваш фан-клуб!</p>

            <div class="card">
                <div class="card-body">
                    <div id="chat-messages" class="chat-messages mb-3">
                        <div class="alert alert-info">
                            Привет! Я AI помощник fan-club.kz. Чем могу помочь?
                        </div>
                    </div>

                    <div class="input-group">
                        <input type="text" id="user-message" class="form-control"
                               placeholder="Введите ваш вопрос..." maxlength="500">
                        <button class="btn btn-primary" id="send-message">Отправить</button>
                    </div>

                    <div class="mt-3">
                        <button class="btn btn-outline-secondary" id="club-help">Помощь с созданием клуба</button>
                        <button class="btn btn-outline-secondary" id="event-ideas">Идеи мероприятий</button>
                        <button class="btn btn-outline-secondary" id="community-tips">Советы по сообществу</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('user-message');
    const sendButton = document.getElementById('send-message');
    const chatMessages = document.getElementById('chat-messages');

    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = isUser ? 'alert alert-primary' : 'alert alert-info';
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function sendMessage(message) {
        addMessage(message, true);

        fetch('/api/ai/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addMessage(data.response);
            } else {
                addMessage('Извините, произошла ошибка. Попробуйте еще раз.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('Извините, произошла ошибка. Попробуйте еще раз.');
        });
    }

    sendButton.addEventListener('click', function() {
        const message = messageInput.value.trim();
        if (message) {
            sendMessage(message);
            messageInput.value = '';
        }
    });

    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const message = messageInput.value.trim();
            if (message) {
                sendMessage(message);
                messageInput.value = '';
            }
        }
    });

    document.getElementById('club-help').addEventListener('click', function() {
        sendMessage('Помоги создать фан-клуб');
    });

    document.getElementById('event-ideas').addEventListener('click', function() {
        sendMessage('Идеи мероприятий для фан-клуба');
    });

    document.getElementById('community-tips').addEventListener('click', function() {
        sendMessage('Как вовлечь участников в фан-клуб');
    });
});
</script>
{% endblock %}
"""

def create_ai_chat_template():
    """Create AI chat template file"""
    template_dir = '/var/www/myapp/eventsite/templates/ai_consultant'
    os.makedirs(template_dir, exist_ok=True)

    template_content = """{% extends 'base.html' %}

{% block title %}AI Консультант - fan-club.kz{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-md-12">
            <h1>🤖 AI Консультант</h1>
            <p class="lead">Помогу создать и развить ваш фан-клуб!</p>

            <div class="card">
                <div class="card-body">
                    <div id="chat-messages" class="chat-messages mb-3">
                        <div class="alert alert-info">
                            Привет! Я AI помощник fan-club.kz. Чем могу помочь?
                        </div>
                    </div>

                    <div class="input-group">
                        <input type="text" id="user-message" class="form-control"
                               placeholder="Введите ваш вопрос..." maxlength="500">
                        <button class="btn btn-primary" id="send-message">Отправить</button>
                    </div>

                    <div class="mt-3">
                        <button class="btn btn-outline-secondary" id="club-help">Помощь с созданием клуба</button>
                        <button class="btn btn-outline-secondary" id="event-ideas">Идеи мероприятий</button>
                        <button class="btn btn-outline-secondary" id="community-tips">Советы по сообществу</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('user-message');
    const sendButton = document.getElementById('send-message');
    const chatMessages = document.getElementById('chat-messages');

    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = isUser ? 'alert alert-primary' : 'alert alert-info';
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function sendMessage(message) {
        addMessage(message, true);

        fetch('/api/ai/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addMessage(data.response);
            } else {
                addMessage('Извините, произошла ошибка. Попробуйте еще раз.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('Извините, произошла ошибка. Попробуйте еще раз.');
        });
    }

    sendButton.addEventListener('click', function() {
        const message = messageInput.value.trim();
        if (message) {
            sendMessage(message);
            messageInput.value = '';
        }
    });

    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const message = messageInput.value.trim();
            if (message) {
                sendMessage(message);
                messageInput.value = '';
            }
        }
    });

    document.getElementById('club-help').addEventListener('click', function() {
        sendMessage('Помоги создать фан-клуб');
    });

    document.getElementById('event-ideas').addEventListener('click', function() {
        sendMessage('Идеи мероприятий для фан-клуба');
    });

    document.getElementById('community-tips').addEventListener('click', function() {
        sendMessage('Как вовлечь участников в фан-клуб');
    });
});
</script>
{% endblock %}
"""

    with open(f'{template_dir}/chat.html', 'w', encoding='utf-8') as f:
        f.write(template_content)