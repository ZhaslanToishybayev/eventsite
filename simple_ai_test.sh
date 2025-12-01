#!/bin/bash

# 🧪 AI Testing Script
echo "🧪 ТЕСТИРОВАНИЕ AI КОНСУЛЬТАНТА"
echo "=============================="

API_URL="http://localhost:8000/api/v1/ai/simplified/interactive/chat/"

send_request() {
    curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$1\", \"user_email\": \"$2\", \"state_id\": $3}"
}

# Тест 1: Статус
echo "1. Проверка статуса..."
status=$(curl -s http://localhost:8000/api/v1/ai/simplified/interactive/status/)
if echo "$status" | grep -q "working"; then
    echo "✅ Статус: РАБОТАЕТ"
else
    echo "❌ Статус: НЕ РАБОТАЕТ"
fi

# Тест 2: Приветствие
echo ""
echo "2. Тест приветствия..."
greeting=$(send_request "Привет" "test@fan-club.kz" "null")
if echo "$greeting" | grep -q "Привет"; then
    echo "✅ Приветствие: РАБОТАЕТ"
else
    echo "❌ Приветствие: НЕ РАБОТАЕТ"
fi

# Тест 3: Создание клуба
echo ""
echo "3. Тест создания клуба..."
create_response=$(send_request "Создать клуб" "test@fan-club.kz" "null")
state_id=$(echo "$create_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['state_id'])")

if [ -n "$state_id" ] && echo "$create_response" | grep -q "создадим твой фан-клуб"; then
    echo "✅ Начало создания: РАБОТАЕТ"
    echo "   State ID: $state_id"
else
    echo "❌ Начало создания: НЕ РАБОТАЕТ"
fi

# Тест 4: Ввод названия
echo ""
echo "4. Тест ввода названия..."
name_response=$(send_request "IT Клуб Алматы" "test@fan-club.kz" "\"$state_id\"")
if echo "$name_response" | grep -q "опиши свой.*клуб"; then
    echo "✅ Ввод названия: РАБОТАЕТ"
else
    echo "❌ Ввод названия: НЕ РАБОТАЕТ"
fi

# Тест 5: Ввод описания
echo ""
echo "5. Тест ввода описания..."
desc_response=$(send_request "Клуб для программистов и технологий" "test@fan-club.kz" "\"$state_id\"")
if echo "$desc_response" | grep -q "категорию относится"; then
    echo "✅ Ввод описания: РАБОТАЕТ"
else
    echo "❌ Ввод описания: НЕ РАБОТАЕТ"
fi

# Тест 6: Ввод категории
echo ""
echo "6. Тест ввода категории..."
cat_response=$(send_request "Технологии" "test@fan-club.kz" "\"$state_id\"")
if echo "$cat_response" | grep -q "в каком городе"; then
    echo "✅ Ввод категории: РАБОТАЕТ"
else
    echo "❌ Ввод категории: НЕ РАБОТАЕТ"
fi

# Тест 7: Ввод города
echo ""
echo "7. Тест ввода города..."
city_response=$(send_request "Алматы" "test@fan-club.kz" "\"$state_id\"")
if echo "$city_response" | grep -q "email для связи"; then
    echo "✅ Ввод города: РАБОТАЕТ"
else
    echo "❌ Ввод города: НЕ РАБОТАЕТ"
fi

# Тест 8: Ввод email
echo ""
echo "8. Тест ввода email..."
email_response=$(send_request "it-club@mail.kz" "test@fan-club.kz" "\"$state_id\"")
if echo "$email_response" | grep -q "Телефон для связи"; then
    echo "✅ Ввод email: РАБОТАЕТ"
else
    echo "❌ Ввод email: НЕ РАБОТАЕТ"
fi

# Тест 9: Ввод телефона
echo ""
echo "9. Тест ввода телефона..."
phone_response=$(send_request "+77011234567" "test@fan-club.kz" "\"$state_id\"")
if echo "$phone_response" | grep -q "Адрес встреч клуба"; then
    echo "✅ Ввод телефона: РАБОТАЕТ"
else
    echo "❌ Ввод телефона: НЕ РАБОТАЕТ"
fi

# Тест 10: Финальный шаг
echo ""
echo "10. Тест финального шага..."
final_response=$(send_request "нет" "test@fan-club.kz" "\"$state_id\"")
if echo "$final_response" | grep -q "успешно создан"; then
    echo "✅ Финальный шаг: РАБОТАЕТ"
else
    echo "❌ Финальный шаг: НЕ РАБОТАЕТ"
fi

# Тест 11: Проверка базы данных
echo ""
echo "11. Проверка базы данных..."
db_result=$(source venv/bin/activate && python manage.py shell << 'EOF'
from clubs.models import Club
clubs = Club.objects.filter(name__icontains='IT Клуб').order_by('-created_at')[:1]
if clubs:
    club = clubs[0]
    print(f"CREATED:{club.name}:{club.category.name}:{club.city.name}")
else:
    print("NOT_FOUND")
EOF
)

if echo "$db_result" | grep -q "CREATED"; then
    echo "✅ База данных: КЛУБ СОЗДАН"
    echo "   $(echo "$db_result" | sed 's/CREATED:/Название: /')"
else
    echo "❌ База данных: КЛУБ НЕ СОЗДАН"
fi

echo ""
echo "🏁 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!"
echo "=============================="