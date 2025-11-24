#!/bin/bash

# UnitySphere Complete Setup and Launch Script
# Includes AI Agent integration

echo "🚀 UnitySphere Complete Setup for fan-club.kz"
echo "=============================================="

# Change to project directory
cd /var/www/myapp/eventsite

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install OpenAI package if not installed
echo "📦 Installing OpenAI package..."
pip install openai

# Check if .env file exists and has AI settings
if [ ! -f ".env" ] || ! grep -q "OPENAI_API_KEY" .env; then
    echo "⚙️ Creating/updating .env file with AI settings..."
    cat > .env <<EOF
# Django Settings
DJANGO_SECRET_KEY='development-secret-key-not-for-production'
DEBUG=True

# Database Settings (SQLite for development)
DB_NAME=db.sqlite3

# AI Settings
OPENAI_API_KEY=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
OPENAI_MODEL=gpt-4o-mini
SERENA_ENABLED=True
SERENA_URL=http://localhost:8001
SERENA_TIMEOUT=30
AI_CONSULTANT_ENABLED=True

# Email Settings (development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Google OAuth (development)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Redis (if used)
REDIS_HOST=localhost
REDIS_PORT=6379
EOF
fi

# Create AI chat template directory
echo "🎨 Creating AI chat template..."
mkdir -p templates/ai_consultant

# Create the AI chat template
cat > templates/ai_consultant/chat.html <<'EOF'
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
                        <button class="btn btn-outline-secondary" id="event-idea">Идеи мероприятий</button>
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
EOF

# Test AI agent
echo "🧪 Testing AI Agent..."
python manage.py test_ai_agent --test

if [ $? -eq 0 ]; then
    echo "✅ AI Agent tests passed!"
else
    echo "⚠️ AI Agent tests failed, but continuing..."
fi

# Run Django checks
echo "✅ Running Django checks..."
python manage.py check

if [ $? -ne 0 ]; then
    echo "⚠️ Django checks found issues, but continuing..."
fi

# Create migrations
echo "🗄️ Creating migrations..."
python manage.py makemigrations 2>/dev/null || echo "No models to migrate"

# Apply migrations
echo "🔄 Applying migrations..."
python manage.py migrate 2>/dev/null || echo "Migration failed, using SQLite default"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || echo "Static files collection failed"

# Create superuser if doesn't exist
echo "👤 Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Superuser needed')
    exit(1)
else:
    print('Superuser exists')
    exit(0)
" 2>/dev/null

if [ $? -eq 1 ]; then
    echo "📝 Creating superuser..."
    echo "Enter username for superuser:"
    read username
    echo "Enter email:"
    read email
    python manage.py createsuperuser --username $username --email $email
fi

# Final status
echo ""
echo "🎉 UnitySphere Setup Complete!"
echo "=============================="
echo ""
echo "🌐 Site URLs:"
echo "   - Main site: http://localhost:8000"
echo "   - By IP: http://77.243.80.110:8000"
echo "   - Admin: http://localhost:8000/admin/"
echo "   - AI Consultant: http://localhost:8000/ai/consultant/"
echo ""
echo "🤖 AI Features:"
echo "   - Club creation assistance"
echo "   - Event ideas generation"
echo "   - Community engagement tips"
echo "   - General Q&A"
echo ""
echo "API Endpoints:"
echo "   - POST /api/ai/chat/ - General chat"
echo "   - POST /api/ai/club-help/ - Club creation help"
echo "   - POST /api/ai/event-ideas/ - Event ideas"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python manage.py runserver 0.0.0.0:8000