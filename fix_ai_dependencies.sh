#!/bin/bash

# 🔧 СКРИПТ: Устранение AI dependency конфликтов

echo "🤖 Устранение AI dependency конфликтов..."

# Создаем упрощенное виртуальное окружение для AI
echo "🐍 Создаем упрощенное виртуальное окружение..."
python3 -m venv venv_ai_simple
source venv_ai_simple/bin/activate

# Устанавливаем только необходимые зависимости
echo "📦 Устанавливаем минимальные AI зависимости..."
pip install openai python-dotenv requests

echo "✅ Упрощенное AI окружение создано!"
echo "📍 Путь: venv_ai_simple/"

# Тестируем AI функциональность
echo "🧪 Тестируем AI функциональность..."
python3 -c "
import openai
import os
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# Проверяем OpenAI
api_key = os.getenv('OPENAI_API_KEY')
if api_key and len(api_key) > 10:
    print('✅ OpenAI API Key найден')
    try:
        client = openai.OpenAI(api_key=api_key)
        print('✅ OpenAI клиент создан')
    except Exception as e:
        print(f'❌ OpenAI клиент: {e}')
else:
    print('❌ OpenAI API Key не найден')

print('✅ AI dependency проверка завершена')
"

echo ""
echo "🎯 Для использования упрощенного AI:"
echo "source venv_ai_simple/bin/activate"
echo "python ai_agent.py"