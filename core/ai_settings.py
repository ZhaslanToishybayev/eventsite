"""
🔧 AI Configuration Settings - Настройки AI интеграции

Этот файл содержит конфигурацию для GPT-4o mini интеграции.
Добавьте этот файл в Django settings для активации AI функций.
"""

# GPT-4o mini API Configuration
OPENAI_API_KEY = "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"
OPENAI_API_BASE = "https://api.openai.com/v1"
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_TEMPERATURE = 0.7
OPENAI_MAX_TOKENS = 1500
OPENAI_TIMEOUT = 30

# AI System Configuration
AI_ENABLED = False  # Отключаем AI при старте для ускорения загрузки
AI_CONSULTANT_ENABLED = False
AI_RECOMMENDATIONS_ENABLED = False
AI_CLUB_CREATION_ENABLED = False

# Rate Limiting
AI_RATE_LIMIT_REQUESTS = 60  # requests per minute
AI_RATE_LIMIT_WINDOW = 60    # seconds

# Caching Configuration
AI_CACHE_TIMEOUT = 300  # 5 minutes
AI_CACHE_ENABLED = True

# Context Configuration
AI_CONTEXT_WINDOW = 10  # Number of previous messages to consider
AI_RECOMMENDATION_LIMIT = 5  # Max recommendations per response
AI_SEARCH_LIMIT = 20  # Max search results

# RAG (Retrieval-Augmented Generation) Configuration
AI_RAG_ENABLED = False  # Отключаем RAG при старте для ускорения
AI_RAG_SIMILARITY_THRESHOLD = 0.7
AI_RAG_MAX_DOCUMENTS = 5

# Logging Configuration
AI_LOG_LEVEL = "INFO"
AI_LOG_REQUESTS = True
AI_LOG_RESPONSES = False  # Set to True for debugging

# Error Handling
AI_RETRY_ATTEMPTS = 3
AI_RETRY_DELAY = 1  # seconds
AI_FALLBACK_ENABLED = True

# Performance Configuration
AI_ASYNC_ENABLED = False  # Отключаем асинхронность для упрощения
AI_BATCH_PROCESSING_ENABLED = False
AI_PARALLEL_REQUESTS = 1  # Уменьшаем количество параллельных запросов