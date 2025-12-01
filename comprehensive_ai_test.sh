#!/bin/bash

echo "🧪 ЗАПУСК КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ AI КОНСУЛЬТАНТА"
echo "================================================================"

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

success_msg() {
    echo -e "${GREEN}✅ $1${NC}"
}

error_msg() {
    echo -e "${RED}❌ $1${NC}"
}

warning_msg() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

info_msg() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

test_msg() {
    echo -e "${PURPLE}🧪 $1${NC}"
}

API_URL="http://localhost:8000/api/v1/ai/simplified/interactive/chat/"
TEST_COUNT=0
PASSED_TESTS=0
FAILED_TESTS=0

send_ai_request() {
    local message="$1"
    local user_email="$2"
    local state_id="$3"
    
    curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$message\", \"user_email\": \"$user_email\", \"state_id\": $state_id}"
}

check_response() {
    local response="$1"
    local expected_pattern="$2"
    local test_name="$3"
    
    TEST_COUNT=$((TEST_COUNT + 1))
    
    if echo "$response" | grep -q "$expected_pattern"; then
        success_msg "Тест '$test_name' ПРОЙДЕН"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        error_msg "Тест '$test_name' ПРОВАЛЕН"
        warning_msg "Ожидалось: $expected_pattern"
        warning_msg "Получено: $(echo "$response" | head -100)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo ""
info_msg "1. ТЕСТИРОВАНИЕ СТАТУСА AI СИСТЕМЫ"
echo "----------------------------------------"

status_response=$(curl -s http://localhost:8000/api/v1/ai/simplified/interactive/status/)
check_response "$status_response" "working" "AI статус"

echo ""
info_msg "2. ТЕСТИРОВАНИЕ БАЗОВЫХ ФУНКЦИЙ"
echo "----------------------------------"

test_msg "Тест 1: Приветствие"
greeting_response=$(send_ai_request "Привет" "test@fan-club.kz" "null")
check_response "$greeting_response" "Привет" "Приветствие"

test_msg "Тест 2: Создание клуба"
create_response=$(send_ai_request "Создать клуб" "test@fan-club.kz" "null")
STATE_ID=$(echo "$create_response" | grep -o '"state_id":"[^"]*"' | cut -d'"' -f4)
check_response "$create_response" "создадим твой фан-клуб" "Команда создания"

echo ""
info_msg "3. ТЕСТИРОВАНИЕ СОЗДАНИЯ КЛУБА"
echo "----------------------------------"

test_msg "Тест 3: Ввод названия"
name_response=$(send_ai_request "IT Клуб Алматы" "test@fan-club.kz" "\"$STATE_ID\"")
check_response "$name_response" "опиши свой.*клуб" "Ввод названия"

test_msg "Тест 4: Ввод описания"
description_response=$(send_ai_request "Это сообщество для программистов и технологий. Мы проводим митапы и хакатоны." "test@fan-club.kz" "\"$STATE_ID\"")
check_response "$description_response" "категорию относится" "Ввод описания"

test_msg "Тест 5: Ввод категории"
category_response=$(send_ai_request "Технологии" "test@fan-club.kz" "\"$STATE_ID\"")
check_response "$category_response" "в каком городе" "Ввод категории"

test_msg "Тест 6: Ввод города"
city_response=$(send_ai_request "Алматы" "test@fan-club.kz" "\"$STATE_ID\"")
check_response "$city_response" "email для связи" "Ввод города"

test_msg "Тест 7: Ввод email"
email_response=$(send_ai_request "it-club@mail.kz" "test@fan-club.kz" "\"$STATE_ID\"")
check_response "$email_response" "Телефон для связи" "Ввод email"

test_msg "Тест 8: Ввод телефона +77011234567"
phone_response=$(send_ai_request "+77011234567" "test@fan-club.kz" "\"$STATE_ID\"")
check_response "$phone_response" "Адрес встреч клуба" "Ввод телефона +7"

test_msg "Тест 9: Ввод адреса"
address_response=$(send_ai_request "нет" "test@fan-club.kz" "\"$STATE_ID\"")
check_response "$address_response" "успешно создан" "Ввод адреса"

echo ""
info_msg "4. ТЕСТИРОВАНИЕ ВАЛИДАЦИИ"
echo "----------------------------"

test_msg "Тест 10: Короткое описание"
short_state=$(send_ai_request "Создать клуб" "test@fan-club.kz" "null" | grep -o '"state_id":"[^"]*"' | cut -d'"' -f4)
short_response=$(send_ai_request "IT Клуб" "test@fan-club.kz" "\"$short_state\"")
short_response=$(send_ai_request "Коротко" "test@fan-club.kz" "\"$short_state\"")
check_response "$short_response" "слишком короткое" "Валидация описания"

echo ""
info_msg "5. ТЕСТИРОВАНИЕ ФОРМ-ПАРСИНГА"
echo "-------------------------------"

test_msg "Тест 11: Форм-парсинг"
form_response=$(send_ai_request "Название клуба: Музыкальная Школа\nОписание клуба: Школа для изучения музыки\nКатегория: Музыка\nГород: Астана\nEmail: music@school.kz\nPhone: +7701234567\nAddress: Астана, центр" "test@fan-club.kz" "null")
check_response "$form_response" "успешно создан" "Форм-парсинг"

echo ""
info_msg "6. ПРОВЕРКА БАЗЫ ДАННЫХ"
echo "---------------------------"

db_check=$(source venv/bin/activate && python manage.py shell << 'EOF'
from clubs.models import Club
clubs = Club.objects.filter(name__icontains='IT Клуб').order_by('-created_at')[:1]
if clubs:
    club = clubs[0]
    print(f"CLUB_FOUND:{club.name}:{club.category.name}:{club.city.name}")
else:
    print("NO_CLUBS_FOUND")
