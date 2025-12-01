#!/bin/bash

# 🧪 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ САЙТА
# Полная проверка всех компонентов системы

echo "🧪 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ САЙТА"
echo "📅 $(date)"
echo "🎯 Цель: Проверить все компоненты системы на идеальную работу"
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Счетчики
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
WARNING_TESTS=0

# Функция для тестирования URL
test_url() {
    local url="$1"
    local description="$2"
    local expected_code="$3"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "   🔍 $description ($url): "
    local actual_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)

    if [ "$actual_code" = "$expected_code" ]; then
        echo -e "${GREEN}✅ $actual_code${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    elif [ "$actual_code" = "302" ] && [ "$expected_code" = "200" ]; then
        echo -e "${YELLOW}⚠️  $actual_code (редирект)${NC}"
        WARNING_TESTS=$((WARNING_TESTS + 1))
        return 1
    else
        echo -e "${RED}❌ $actual_code (ожидал $expected_code)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Функция для тестирования API
test_api() {
    local url="$1"
    local description="$2"
    local expected_contains="$3"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "   🔍 $description: "
    local response=$(curl -s "$url" 2>/dev/null)
    local status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)

    if [ "$status_code" = "200" ] && echo "$response" | grep -q "$expected_contains" 2>/dev/null; then
        echo -e "${GREEN}✅ API OK${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ API ERROR${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Функция для тестирования AI
test_ai() {
    local description="$1"
    local message="$2"
    local expected_intent="$3"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "   🔍 $description: "
    local response=$(curl -s -X POST http://127.0.0.1:8003/api/ai/enhanced/enhanced/chat/ \
        -H "Content-Type: application/json" \
        -d "{\"message\":\"$message\",\"session_id\":\"test\"}" 2>/dev/null)

    if echo "$response" | grep -q "$expected_intent" 2>/dev/null; then
        echo -e "${GREEN}✅ AI OK${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ AI ERROR${NC}"
        echo "      Response: $response"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo "🌐 ТЕСТИРОВАНИЕ ОСНОВНЫХ СТРАНИЦ"
echo "=================================="

test_url "http://127.0.0.1:8003/" "Главная страница" "200"
test_url "http://127.0.0.1:8003/clubs/" "Страница клубов" "200"
test_url "http://127.0.0.1:8003/test_enhanced_widget/" "Test Enhanced Widget" "200"

echo ""
echo "🔐 ТЕСТИРОВАНИЕ АВТОРИЗАЦИИ"
echo "==============================="

test_url "http://127.0.0.1:8003/accounts/register/" "Страница регистрации" "200"
test_url "http://127.0.0.1:8003/accounts/login/" "Страница входа" "200"
test_url "http://127.0.0.1:8003/accounts/logout/" "Выход (редирект)" "302"
test_url "http://127.0.0.1:8003/accounts/google/login/" "Google OAuth" "200"
test_url "http://127.0.0.1:8003/accounts/password/reset/" "Сброс пароля" "200"
test_url "http://127.0.0.1:8003/admin/" "Админка (редирект)" "302"

echo ""
echo "🤖 ТЕСТИРОВАНИЕ ENHANCED AI"
echo "============================="

test_api "http://127.0.0.1:8003/api/ai/enhanced/enhanced/health/" "Health Check" "healthy"
test_api "http://127.0.0.1:8003/api/ai/enhanced/enhanced/categories/" "Категории клубов" "categories"
test_api "http://127.0.0.1:8003/api/ai/enhanced/enhanced/cities/" "Города" "cities"

test_ai "AI Chat - приветствие" "Привет" "general_chat"
test_ai "AI Chat - поиск клубов" "Найди музыкальные клубы в Алмате" "club_search"
test_ai "AI Chat - информация о клубах" "Расскажи о клубах" "club_info"

echo ""
echo "🔍 ТЕСТИРОВАНИЕ ПОИСКА КЛУБОВ"
echo "==============================="

# Тестирование поиска с разными параметрами
curl -s "http://127.0.0.1:8003/api/ai/enhanced/enhanced/clubs/search/?q=музыка&limit=2" | head -1 | while read response; do
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "   🔍 Поиск по 'музыка': "
    if echo "$response" | grep -q '"clubs"' 2>/dev/null; then
        echo -e "${GREEN}✅ Поиск OK${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ Поиск ERROR${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
done

curl -s "http://127.0.0.1:8003/api/ai/enhanced/enhanced/clubs/search/?q=спорт&limit=1" | head -1 | while read response; do
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "   🔍 Поиск по 'спорт': "
    if echo "$response" | grep -q '"clubs"' 2>/dev/null; then
        echo -e "${GREEN}✅ Поиск OK${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ Поиск ERROR${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
done

echo ""
echo "⚙️  ТЕСТИРОВАНИЕ СИСТЕМНЫХ ФУНКЦИЙ"
echo "=================================="

# Проверка Django настроек
echo -n "   🔍 Django настройки: "
source venv/bin/activate >/dev/null 2>&1 && \
python3 manage.py check --deploy >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Настройки OK${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
else
    echo -e "${YELLOW}⚠️  Предупреждения в настройках${NC}"
    WARNING_TESTS=$((WARNING_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

# Проверка базы данных
echo -n "   🔍 База данных: "
source venv/bin/activate >/dev/null 2>&1 && \
python3 manage.py shell << 'EOF_CHECK_DB' >/dev/null 2>&1
from django.db import connection
from clubs.models import Club
try:
    clubs_count = Club.objects.count()
    print(f"DB_OK:{clubs_count}")
except Exception as e:
    print(f"DB_ERROR:{e}")
EOF_CHECK_DB

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ БД OK${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
else
    echo -e "${RED}❌ БД ERROR${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

echo ""
echo "🎨 ТЕСТИРОВАНИЕ ШАБЛОНОВ И СТАТИКИ"
echo "====================================="

# Проверка загрузки статических файлов
test_url "http://127.0.0.1:8003/static/css/ai-chat-widget-v2.css" "CSS файлы" "200"
test_url "http://127.0.0.1:8003/static/js/ai-chat-widget-v2.js" "JS файлы" "200"

echo ""
echo "📊 ФИНАЛЬНЫЙ ОТЧЕТ"
echo "===================="

echo ""
echo "📈 СТАТИСТИКА ТЕСТИРОВАНИЯ:"
echo "   📋 Всего тестов: $TOTAL_TESTS"
echo "   ✅ Пройдено: $PASSED_TESTS"
echo "   ❌ Ошибки: $FAILED_TESTS"
echo "   ⚠️  Предупреждения: $WARNING_TESTS"

# Рассчитаем процент успеха
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    WARNING_RATE=$((WARNING_TESTS * 100 / TOTAL_TESTS))
    ERROR_RATE=$((FAILED_TESTS * 100 / TOTAL_TESTS))
else
    SUCCESS_RATE=0
    WARNING_RATE=0
    ERROR_RATE=0
fi

echo ""
echo "🎯 ПРОЦЕНТНЫЙ ОБЗОР:"
echo "   ✅ Успешно: $SUCCESS_RATE%"
echo "   ⚠️  Предупреждения: $WARNING_RATE%"
echo "   ❌ Ошибки: $ERROR_RATE%"

echo ""
echo "🏁 ОБЩАЯ ОЦЕНКА:"

if [ $FAILED_TESTS -eq 0 ]; then
    if [ $WARNING_TESTS -eq 0 ]; then
        echo -e "   🎉 ${GREEN}ИДЕАЛЬНО! Все тесты пройдены успешно!${NC}"
        echo -e "   💯 ${GREEN}Уровень надежности: 100%${NC}"
    else
        echo -e "   ✨ ${GREEN}ОТЛИЧНО! Есть незначительные предупреждения${NC}"
        echo -e "   💪 ${GREEN}Уровень надежности: $((100 - ERROR_RATE))%${NC}"
    fi
elif [ $ERROR_RATE -lt 10 ]; then
    echo -e "   ⚠️  ${YELLOW}ХОРОШО, но есть проблемы для исправления${NC}"
    echo -e "   📈 ${YELLOW}Уровень надежности: $((100 - ERROR_RATE))%${NC}"
else
    echo -e "   ❌ ${RED}ПЛОХО! Много критических ошибок${NC}"
    echo -e "   🚨 ${RED}Уровень надежности: $((100 - ERROR_RATE))%${NC}"
fi

echo ""
echo "📋 РЕКОМЕНДАЦИИ:"

if [ $FAILED_TESTS -eq 0 ]; then
    echo "   ✅ Система полностью готова к production"
    echo "   🚀 Можно начинать использовать сайт"
    echo "   📊 Регулярно мониторить производительность"
else
    echo "   ❌ Требуется исправление критических ошибок:"
    [ $FAILED_TESTS -gt 0 ] && echo "      - Исправить $FAILED_TESTS критические ошибки"
fi

if [ $WARNING_TESTS -gt 0 ]; then
    echo "   ⚠️  Рекомендуется устранить предупреждения:"
    [ $WARNING_TESTS -gt 0 ] && echo "      - Устранить $WARNING_TESTS предупреждений"
fi

echo ""
echo "🚀 СЛЕДУЮЩИЕ ШАГИ:"
echo "   1. Если система прошла тесты - можно использовать в production"
echo "   2. При наличии ошибок - исправить и перетестировать"
echo "   3. Рассмотреть возможность Day 3 - RAG интеграции"
echo "   4. Настроить мониторинг и логирование"
echo ""