# 🚀 RAG Enhanced AI Consultant - Setup Guide

## Обзор

Руководство по установке и настройке RAG (Retrieval-Augmented Generation) улучшенного ИИ-консультанта UnitySphere v2.1.

## 📋 Что добавлено:

### 🔍 **Векторная база знаний**
- **ChromaDB** - локальная векторная база данных
- **FAISS** - быстрый поиск похожих векторов
- **Sentence Transformers** - эмбеддинги текста

### 🧠 **Улучшенная контекстуализация**
- Анализ интентов и сущностей сообщений
- Персонализация на основе истории пользователя
- Обогащение контента из базы знаний

### 📊 **Предиктивная аналитика**
- Прогнозирование следующих вопросов
- Оценка успешности консультации
- Рекомендации по улучшению

### 🤖 **RAG-агенты**
- Интегрированные агенты с доступом к базе знаний
- Обогащенные промпты с контекстом
- Более точные и релевантные ответы

---

## 🛠️ Установка

### 1. Установка зависимостей

```bash
# Активация виртуального окружения
source venv/bin/activate

# Установка RAG зависимостей
pip install -r requirements-ai.txt

# Дополнительные зависимости для NLP
pip install spacy
python -m spacy download ru_core_news_sm  # Русская модель spaCy

# Установка зависимостей для машинного обучения
pip install scikit-learn nltk
python -m nltk.downloader punkt
```

### 2. Настройка переменных окружения

Добавьте в `.env` файл:

```bash
# RAG Configuration
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
CHROMA_DB_PATH=./chroma_db
RAG_CONFIDENCE_THRESHOLD=0.7
RAG_MAX_RESULTS=5

# Enhanced Analytics
AI_ANALYTICS_ENABLED=True
PREDICTIVE_ENGINE_ENABLED=True
ANALYTICS_CACHE_TIMEOUT=3600

# Performance
AI_CACHE_TIMEOUT=300
RAG_CACHE_TIMEOUT=1800
```

### 3. Создание директорий

```bash
# Создание директории для векторной базы
mkdir -p ./chroma_db
chmod 755 ./chroma_db

# Создание лог-директории
mkdir -p ./logs/ai_consultant
```

### 4. Индексация знаний

```bash
# Полная индексация всех знаний
python manage.py index_knowledge --rebuild --verbose

# Только документация
python manage.py index_knowledge --docs-only

# Только клубы
python manage.py index_knowledge --clubs-only

# Проверка статуса индексации
python manage.py index_knowledge --verbose
```

---

## 🔧 Конфигурация

### 1. Настройка Django

В `core/settings.py` добавьте:

```python
# RAG Settings
RAG_SETTINGS = {
    'EMBEDDING_MODEL': os.getenv('RAG_EMBEDDING_MODEL', 'all-MiniLM-L6-v2'),
    'CHROMA_DB_PATH': os.getenv('CHROMA_DB_PATH', './chroma_db'),
    'CONFIDENCE_THRESHOLD': float(os.getenv('RAG_CONFIDENCE_THRESHOLD', 0.7)),
    'MAX_RESULTS': int(os.getenv('RAG_MAX_RESULTS', 5)),
    'ENABLE_CACHING': True,
    'CACHE_TIMEOUT': int(os.getenv('RAG_CACHE_TIMEOUT', 1800)),
}

# Analytics Settings
ANALYTICS_SETTINGS = {
    'ENABLED': os.getenv('AI_ANALYTICS_ENABLED', 'True').lower() == 'true',
    'PREDICTIVE_ENGINE': os.getenv('PREDICTIVE_ENGINE_ENABLED', 'True').lower() == 'true',
    'CACHE_TIMEOUT': int(os.getenv('ANALYTICS_CACHE_TIMEOUT', 3600)),
    'BATCH_SIZE': 100,
}
```

### 2. Обновление URL

В `core/urls.py` добавьте новые эндпоинты:

```python
# Enhanced AI Consultant URLs
from ai_consultant.api import urls_v2

path('api/v1/ai/', include(urls_v2)),
```

---

## 📊 Использование

### 1. API Эндпоинты

```python
# Основной RAG чат
POST /api/v1/ai/chat/v2/
{
    "message": "Как создать спортивный клуб?",
    "session_id": "optional-session-uuid"
}

# Создание RAG сессии
POST /api/v1/ai/sessions/v2/create/

# Получение аналитики
GET /api/v1/ai/analytics/v2/?period=week&user_id=123

# Перестроение индекса
POST /api/v1/ai/rebuild-index/
```

### 2. Использование в коде

```python
from ai_consultant.services_v2 import AIConsultantServiceV2

# Создание RAG сервис
ai_service = AIConsultantServiceV2()

# Отправка сообщения с RAG
response = ai_service.send_message(session, "Помоги найти клуб по программированию")

# Получение аналитики
analytics = ai_service.get_comprehensive_analytics(period='week')

# Перестроение индекса
result = ai_service.rebuild_knowledge_index()
```

### 3. RAG в агентах

```python
from ai_consultant.agents.specialists.club_agent import ClubAgent

# Создание агента с RAG
agent = ClubAgent()

# Получение обогащенного промпта
prompt = agent.get_system_prompt(
    user_context=user_profile,
    rag_context=retrieved_knowledge
)
```

---

## 📈 Мониторинг и аналитика

### 1. Метрики производительности

```python
# Получение метрик RAG
rag_metrics = {
    'query_confidence': 0.85,        # Уверенность в релевантности
    'retrieval_time': 0.15,           # Время поиска (сек)
    'cache_hit_rate': 0.78,           # Попаданий в кэш
    'index_size': 1500,               # Размер индекса
    'avg_results': 3.2                # Среднее количество результатов
}
```

### 2. Аналитика использования

```python
# Комплексная аналитика
analytics = {
    'overall_metrics': {
        'total_sessions': 1250,
        'avg_rag_confidence': 0.82,
        'success_rate': 0.89
    },
    'predictions': {
        'next_question_accuracy': 0.75,
        'satisfaction_prediction': 0.87
    },
    'recommendations': [
        'Expand documentation in technical topics',
        'Improve response time for club queries'
    ]
}
```

### 3. Логирование

```python
# Включение детального логирования
import logging
logging.getLogger('ai_consultant').setLevel(logging.INFO)

# Просмотр логов
tail -f logs/ai_consultant/rag_service.log
tail -f logs/ai_consultant/enhanced_analytics.log
```

---

## ⚡ Оптимизация

### 1. Кэширование

```python
# Настройка Redis для кэширования
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 2. Индексация

```python
# Оптимальные настройки для больших объемов
RAG_SETTINGS.update({
    'BATCH_SIZE': 1000,              # Размер пакета индексации
    'INDEXING_WORKERS': 4,           # Количество воркеров
    'EMBEDDING_BATCH_SIZE': 32,      # Размер батча для эмбеддингов
})
```

### 3. Производительность

```python
# Мониторинг производительности
import cProfile
cProfile.run('ai_service.send_message(session, message)', sort='cumulative')
```

---

## 🔧 Тестирование

### 1. Unit тесты

```bash
# Тестирование RAG сервиса
python manage.py test ai_consultant.tests.test_rag_service

# Тестирование аналитики
python manage.py test ai_consultant.tests.test_enhanced_analytics

# Тестирование агентов
python manage.py test ai_consultant.tests.test_agents
```

### 2. Интеграционные тесты

```python
# Тестирование полного цикла
def test_rag_integration():
    service = AIConsultantServiceV2()
    session = service.create_chat_session(user)

    response = service.send_message(
        session,
        "Какие есть клубы по программированию?"
    )

    assert 'club' in response['response'].lower()
    assert response['enhanced_context']['rag_confidence'] > 0.5
```

---

## 🚨 Troubleshooting

### 1. Проблемы с ChromaDB

```bash
# Очистка поврежденной базы
rm -rf ./chroma_db
python manage.py index_knowledge --rebuild

# Проверка прав доступа
ls -la ./chroma_db
chmod 755 ./chroma_db
```

### 2. Проблемы с эмбеддингами

```python
# Проверка модели
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("тест")
print(f"Embedding shape: {embedding.shape}")
```

### 3. Низкая уверенность RAG

```python
# Понижение порога уверенности
RAG_SETTINGS['CONFIDENCE_THRESHOLD'] = 0.5

# Расширение базы знаний
python manage.py index_knowledge --rebuild --verbose
```

---

## 📚 Документация

### API Документация:
- `GET /api/v1/ai/docs/` - Swagger документация
- `/ai-chat-demo-v2/` - Демо интерфейс с RAG

### Логи:
- `/logs/ai_consultant/rag_service.log` - RAG сервис
- `/logs/ai_consultant/enhanced_analytics.log` - Аналитика
- `/logs/ai_consultant/context_analyzer.log` - Анализ контекста

---

## 🔄 Обновление

### Обновление индекса:

```bash
# Ежедневное обновление
0 2 * * * cd /path/to/project && python manage.py index_knowledge --clubs-only

# Еженедельное полное перестроение
0 3 * * 0 cd /path/to/project && python manage.py index_knowledge --rebuild
```

### Версионирование:

```python
# Проверка версии
from ai_consultant.services_v2 import AIConsultantServiceV2
service = AIConsultantServiceV2()
print(f"Version: {service.VERSION}")  # v2.1.0
```

---

## 🎯 Следующие шаги

1. **Мониторинг производительности** - Настройка Grafana/Prometheus
2. **A/B тестирование** - Сравнение с предыдущей версией
3. **Расширение базы знаний** - Добавление пользовательского контента
4. **Мультиязычность** - Поддержка других языков
5. **Видео-аналитика** - Анализ видеосодержимого

---

## 📞 Поддержка

- **Документация**: `AI_CONSULTANT_README.md`
- **Технические вопросы**: GitHub Issues
- **Обновления**: `CHANGELOG.md`

**Enjoy your enhanced AI consultant! 🎉**