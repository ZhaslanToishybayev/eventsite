#!/bin/bash

# 🚀 РАБОЧИЙ ЗАПУСК DJANGO СЕРВИСА

echo "🚀 РАБОЧИЙ ЗАПУСК DJANGO СЕРВИСА"
echo "=================================="
echo ""

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# 1. Активируем виртуальное окружение
echo "1. ПОДГОТОВКА ОКРУЖЕНИЯ"
echo "-------------------------"

source venv/bin/activate
print_status "Виртуальное окружение активировано"

# Устанавливаем переменные окружения
export DJANGO_SETTINGS_MODULE=core.settings
export DEBUG=False
export ALLOWED_HOSTS=fan-club.kz,www.fan-club.kz,localhost,127.0.0.1

print_status "Переменные окружения установлены"

# 2. Проверяем Django
echo ""
echo "2. ПРОВЕРКА DJANGO"
echo "-------------------"

python manage.py check --deploy 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "Django проверка пройдена"
else
    print_warning "Django проверка не пройдена, но продолжаем"
fi

# 3. Проверяем порт
echo ""
echo "3. ПРОВЕРКА ПОРТА 8000"
echo "----------------------"

if lsof -i :8000 > /dev/null 2>&1; then
    print_warning "Порт 8000 занят, освобождаем..."
    sudo lsof -ti :8000 | xargs sudo kill -9 > /dev/null 2>&1 || true
fi

if ! lsof -i :8000 > /dev/null 2>&1; then
    print_status "Порт 8000 свободен"
else
    print_error "Порт 8000 занят и не может быть освобожден"
    exit 1
fi

# 4. Запускаем Django
echo ""
echo "4. ЗАПУСК DJANGO"
echo "-----------------"

print_info "Запускаю Django development server..."

# Запускаем Django в фоновом режиме
nohup python manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &
DJANGO_PID=$!

echo "🌐 Django запущен в фоновом режиме (PID: $DJANGO_PID)"

# Ждем запуска
sleep 3

# Проверяем, работает ли Django
if kill -0 $DJANGO_PID 2>/dev/null; then
    print_status "Django процесс запущен"

    # Проверяем доступность
    echo ""
    echo "5. ПРОВЕРКА ДОСТУПНОСТИ"
    echo "------------------------"

    sleep 2

    # Проверяем локальную доступность
    if curl -s --connect-timeout 5 http://127.0.0.1:8000 > /dev/null; then
        print_status "Django доступен локально"
    else
        print_error "Django не доступен локально"
        echo "📋 Логи Django:"
        tail -20 django.log
        kill $DJANGO_PID 2>/dev/null
        exit 1
    fi

    # Проверяем AI API
    echo ""
    echo "🤖 Тестируем AI API..."
    api_response=$(curl -s --connect-timeout 5 -X POST \
        -H "Content-Type: application/json" \
        -d '{"message": "Привет"}' \
        http://127.0.0.1:8000/api/v1/ai/chat/ 2>/dev/null)

    if [ $? -eq 0 ] && [ -n "$api_response" ]; then
        print_status "AI API работает"
        echo "💬 Пример ответа: $(echo $api_response | head -c 100)..."
    else
        print_warning "AI API暂时 недоступен"
    fi

    echo ""
    echo "🎉 DJANGO УСПЕШНО ЗАПУЩЕН!"
    echo "=========================="
    echo ""
    echo "📊 Статус:"
    echo "• Django PID: $DJANGO_PID"
    echo "• Port: 8000"
    echo "• Status: Running"
    echo ""
    echo "🌐 Доступ:"
    echo "• Локально: http://127.0.0.1:8000"
    echo "• Через Nginx: https://fan-club.kz"
    echo ""
    echo "🔧 Управление:"
    echo "• Остановить: kill $DJANGO_PID"
    echo "• Логи: tail -f django.log"
    echo "• Перезапуск: kill $DJANGO_PID && запустить скрипт снова"
    echo ""
    echo "💡 Django работает в фоновом режиме!"
    echo "   Для остановки используйте: kill $DJANGO_PID"

    # Сохраняем PID для будущих операций
    echo $DJANGO_PID > django.pid

else
    print_error "Django не запустился"
    echo "📋 Логи Django:"
    if [ -f django.log ]; then
        tail -20 django.log
    fi
    exit 1
fi