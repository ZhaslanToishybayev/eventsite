# 🤖 AI Club Consultant API Documentation

## Overview

AI Club Consultant API provides intelligent consultation services for clubs and events using GPT-4o mini integration. The API offers advanced features including club recommendations, AI-powered search, and conversational club creation.

## Base URL

```
https://your-domain.com/api/ai/
```

## Authentication

Currently, most endpoints are open for testing. In production, implement API key authentication by adding `Authorization` header:

```
Authorization: Bearer your-api-key
```

## Rate Limiting

- 60 requests per minute per IP
- 1000 requests per day per user (if authenticated)

## API Endpoints

### 1. 🤖 Main AI Consultation

#### POST `/consult/`

Main endpoint for AI consultations about clubs, events, and recommendations.

**Request:**
```json
{
    "message": "Найди музыкальные клубы в Алматы для начинающих",
    "user_id": 123,
    "location": "Алматы"
}
```

**Response:**
```json
{
    "status": "success",
    "response": {
        "type": "recommendations",
        "content": "🎯 Вот подходящие клубы, которые я нашел:\n\n1. **Музыкальная студия**...",
        "clubs": [
            {
                "id": "uuid",
                "name": "Название клуба",
                "description": "Описание",
                "city": "Город",
                "members_count": 25,
                "relevance_score": 9.5
            }
        ],
        "suggestions": [
            "Расскажи подробнее о первом клубе",
            "Показать больше клубов"
        ]
    },
    "timestamp": "2024-11-27T21:45:00Z"
}
```

### 2. 🔍 AI-Powered Club Search

#### GET `/clubs/search/`

Advanced club search with AI-powered filtering and semantic matching.

**Parameters:**
- `q` (string): Search query (name, description, activities)
- `city` (string): City filter
- `category` (string): Category filter
- `limit` (number): Results limit (default: 10, max: 50)

**Example:**
```
GET /api/ai/clubs/search/?q=музыка&city=Алматы&limit=5
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "clubs": [
            {
                "id": "uuid",
                "name": "Музыкальный клуб",
                "description": "Занятия музыкой для всех уровней",
                "city": {
                    "id": "uuid",
                    "name": "Алматы"
                },
                "category": {
                    "id": "uuid",
                    "name": "Музыка"
                },
                "members_count": 45,
                "activities": "Игра на инструментах, пение, теория музыки",
                "skills_developed": "Музыкальное слух, ритм, игра на инструментах",
                "target_audience": "18-35 лет",
                "is_active": true,
                "created_at": "2024-01-15T10:30:00Z",
                "logo": "https://...",
                "email": "music@example.com",
                "phone": "+7 (701) 123-45-67",
                "address": "ул. Абая 123",
                "likes_count": 120,
                "partners_count": 5
            }
        ],
        "total": 25,
        "search_info": {
            "query": "музыка",
            "city": "Алматы",
            "results_count": 5,
            "limit": 5
        }
    }
}
```

### 3. 🎯 AI Club Recommendations

#### POST `/clubs/recommend/`

Personalized club recommendations based on user interests and preferences.

**Request:**
```json
{
    "interests": ["музыка", "пение", "инструменты"],
    "location": "Алматы",
    "user_id": 123,
    "preferences": {
        "age_group": "18-35",
        "activity_level": "средний",
        "experience_level": "начинающий"
    }
}
```

**Response:**
```json
{
    "status": "success",
    "recommendations": [
        {
            "club": {
                "id": "uuid",
                "name": "Музыкальная студия",
                "description": "Описание клуба",
                "city": "Алматы",
                "category": "Музыка",
                "members_count": 45,
                "logo": "https://..."
            },
            "relevance_score": 9.5,
            "reasons": [
                "📍 В вашем городе (Алматы)",
                "🎯 По интересам: музыка, пение",
                "👥 Популярный клуб (45 участников)"
            ],
            "suggested_questions": [
                "Расскажи подробнее о Музыкальная студия",
                "Какие мероприятия проводит Музыкальная студия?",
                "Для кого подходит Музыкальная студия?"
            ]
        }
    ],
    "total_found": 15,
    "criteria": {
        "interests": ["музыка", "пение", "инструменты"],
        "location": "Алматы",
        "preferences": {
            "age_group": "18-35",
            "activity_level": "средний"
        }
    }
}
```

### 4. 🤝 Conversational Club Creation

#### POST `/club/create/`

Interactive club creation through AI conversation.

**Request:**
```json
{
    "action": "start|continue|confirm|cancel",
    "user_id": 123,
    "data": {
        "name": "Музыкальный клуб",
        "description": "Занятия музыкой для начинающих",
        "city": "Алматы",
        "category": "Музыка",
        "target_audience": "18-35 лет, начинающие"
    }
}
```

**Response:**
```json
{
    "status": "success",
    "response": {
        "stage": "name|description|city|category|target_audience|confirmation|completed|error",
        "content": "1. Какое название вы хотите дать вашему клубу?",
        "input_placeholder": "Введите название клуба",
        "suggestions": [
            "Музыкальный клуб",
            "Спортивная секция",
            "IT-сообщество"
        ],
        "club_id": "uuid",  // Only for completed stage
        "club_name": "Название клуба"  // Only for completed stage
    }
}
```

**Creation Flow:**
1. **start**: Begin club creation
2. **continue**: Provide next piece of information
3. **confirm**: Confirm all details and create club
4. **cancel**: Cancel creation process

### 5. 📊 API Health Check

#### GET `/health/`

Check API availability and system status.

**Response:**
```json
{
    "status": "success",
    "ai_available": true,
    "models": ["gpt-4o-mini"],
    "features": [
        "consultation",
        "recommendation",
        "club_search",
        "club_creation"
    ],
    "database_status": "connected",
    "timestamp": "2024-11-27T21:45:00Z"
}
```

## Error Responses

All endpoints return standardized error responses:

```json
{
    "status": "error",
    "message": "Описание ошибки",
    "timestamp": "2024-11-27T21:45:00Z"
}
```

**Common Error Codes:**
- `400`: Invalid request data
- `401`: Authentication required
- `403`: Access forbidden
- `429`: Rate limit exceeded
- `500`: Internal server error
- `503`: Service temporarily unavailable

## Frontend Integration Example

### JavaScript Example
```javascript
class AIConsultantAPI {
    constructor(baseUrl = '/api/ai') {
        this.baseUrl = baseUrl;
    }

    async consult(message, userId = null, location = null) {
        const response = await fetch(`${this.baseUrl}/consult/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message, user_id: userId, location })
        });
        return await response.json();
    }

    async searchClubs(query, city = null, limit = 10) {
        const params = new URLSearchParams({ q: query, limit: limit.toString() });
        if (city) params.append('city', city);

        const response = await fetch(`${this.baseUrl}/clubs/search/?${params}`);
        return await response.json();
    }

    async getRecommendations(interests, location = null, userId = null) {
        const response = await fetch(`${this.baseUrl}/clubs/recommend/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ interests, location, user_id: userId })
        });
        return await response.json();
    }

    async createClub(action, userId, data = {}) {
        const response = await fetch(`${this.baseUrl}/club/create/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action, user_id: userId, data })
        });
        return await response.json();
    }
}

// Usage
const aiAPI = new AIConsultantAPI();

// AI consultation
const response = await aiAPI.consult("Найди танцевальные клубы в Алматы");
console.log(response.response.content);

// Search clubs
const searchResult = await aiAPI.searchClubs("танцы", "Алматы");
console.log(searchResult.data.clubs);

// Get recommendations
const recommendations = await aiAPI.getRecommendations(["танцы", "фитнес"], "Алматы");
console.log(recommendations.recommendations);

// Create club
let creationResult = await aiAPI.createClub("start", 123);
console.log(creationResult.response.content);

creationResult = await aiAPI.createClub("continue", 123, {
    name: "Танцевальный клуб",
    description: "Занятия танцами для всех уровней"
});
console.log(creationResult.response.stage);
```

### Widget Integration
```html
<div id="ai-consultant-widget">
    <div id="ai-chat-container">
        <div id="ai-messages"></div>
        <div id="ai-input">
            <input type="text" id="ai-message-input" placeholder="Задайте вопрос...">
            <button id="ai-send-btn">Отправить</button>
        </div>
    </div>
</div>

<script>
class AIConsultantWidget {
    constructor(apiUrl = '/api/ai') {
        this.apiUrl = apiUrl;
        this.userId = null; // Set from backend
        this.location = null; // Get from geolocation or user input

        this.initializeEventListeners();
    }

    async sendMessage() {
        const messageInput = document.getElementById('ai-message-input');
        const message = messageInput.value.trim();

        if (!message) return;

        this.addMessage('user', message);
        messageInput.value = '';

        try {
            const response = await fetch(`${this.apiUrl}/consult/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message,
                    user_id: this.userId,
                    location: this.location
                })
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.addMessage('ai', result.response.content);

                // Handle different response types
                if (result.response.type === 'recommendations' && result.response.clubs) {
                    this.displayClubRecommendations(result.response.clubs);
                }

                if (result.response.suggestions) {
                    this.displayQuickSuggestions(result.response.suggestions);
                }
            }
        } catch (error) {
            this.addMessage('ai', 'Извините, произошла ошибка. Пожалуйста, попробуйте позже.');
        }
    }

    addMessage(role, content) {
        const messagesContainer = document.getElementById('ai-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `ai-message ${role}`;
        messageDiv.textContent = content;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Additional methods for UI interactions...
}

// Initialize widget
const widget = new AIConsultantWidget();
</script>
```

## Testing the API

### Using curl

```bash
# Health check
curl https://your-domain.com/api/ai/health/

# AI consultation
curl -X POST https://your-domain.com/api/ai/consult/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Найди музыкальные клубы в Алматы", "location": "Алматы"}'

# Search clubs
curl "https://your-domain.com/api/ai/clubs/search/?q=музыка&city=Алматы&limit=5"

# Get recommendations
curl -X POST https://your-domain.com/api/ai/clubs/recommend/ \
  -H "Content-Type: application/json" \
  -d '{"interests": ["музыка", "пение"], "location": "Алматы"}'
```

### Using Postman

1. Import the collection from `ai_consultant_api.postman_collection.json`
2. Set your base URL in environment variables
3. Test each endpoint with different parameters

## Best Practices

### 1. Rate Limiting
- Implement client-side rate limiting
- Cache responses when appropriate
- Use debounce for search inputs

### 2. Error Handling
- Always check response status
- Provide user-friendly error messages
- Implement retry logic for failed requests

### 3. User Experience
- Show loading indicators
- Provide quick suggestions
- Implement smart defaults
- Support keyboard navigation

### 4. Security
- Validate all input data
- Implement CSRF protection
- Use HTTPS in production
- Add API key authentication

## Future Enhancements

Planned features for future versions:

1. **Advanced NLP Processing**
   - Sentiment analysis
   - Intent recognition
   - Entity extraction

2. **Enhanced Recommendations**
   - Machine learning algorithms
   - Collaborative filtering
   - Content-based filtering

3. **Voice Integration**
   - Speech-to-text
   - Text-to-speech
   - Voice commands

4. **Analytics & Insights**
   - User behavior tracking
   - Recommendation effectiveness
   - Search analytics

## Support

For API support and questions:
- Email: ai-support@your-domain.com
- Documentation: https://your-domain.com/docs/ai-api
- Status: https://status.your-domain.com

---

*Last updated: November 27, 2024*