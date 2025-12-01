#!/usr/bin/env python3
import re
import os

# Проверим все JavaScript файлы на синтаксические ошибки
js_files = [
    '/var/www/myapp/eventsite/static/js/ai-chat-widget-v2.js',
    '/var/www/myapp/eventsite/static/js/club-creation-agent-widget.js',
    '/var/www/myapp/eventsite/static/js/enhanced-ai-widget.js',
    '/var/www/myapp/eventsite/static/js/ai-chat-widget.js',
    '/var/www/myapp/eventsite/static/js/actionable-ai-widget.js',
    '/var/www/myapp/eventsite/static/js/ai-chat-widget-standalone.js',
    '/var/www/myapp/eventsite/static/js/ai-widget-updater.js'
]

def check_js_syntax(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        issues = []

        # Проверка несбалансированных скобок
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            issues.append(f'Несбалансированные фигурные скобки: {open_braces} открыты, {close_braces} закрыты')

        open_parens = content.count('(')
        close_parens = content.count(')')
        if open_parens != close_parens:
            issues.append(f'Несбалансированные круглые скобки: {open_parens} открыты, {close_parens} закрыты')

        open_brackets = content.count('[')
        close_brackets = content.count(']')
        if open_brackets != close_brackets:
            issues.append(f'Несбалансированные квадратные скобки: {open_brackets} открыты, {close_brackets} закрыты')

        # Поиск потенциальных проблем
        for i, line in enumerate(lines, 1):
            # Проверка на незакрытые функции
            if re.search(r'function\s+\w*\s*\([^)]*\)\s*$', line.strip()):
                issues.append(f'Строка {i}: Потенциально незакрытая функция: {line.strip()}')

            # Проверка на незакрытые if/for/while
            if re.search(r'(if|for|while)\s*\([^)]*\)\s*$', line.strip()):
                issues.append(f'Строка {i}: Потенциально незакрытый оператор: {line.strip()}')

        return issues, len(lines)

    except Exception as e:
        return [f'Ошибка чтения файла: {e}'], 0

print('=== ПРОВЕРКА JAVASCRIPT ФАЙЛОВ НА СИНТАКСИЧЕСКИЕ ОШИБКИ ===\n')

for file_path in js_files:
    if os.path.exists(file_path):
        issues, line_count = check_js_syntax(file_path)
        print(f'{os.path.basename(file_path)} ({line_count} строк):')
        if issues:
            for issue in issues:
                print(f'  ❌ {issue}')
        else:
            print(f'  ✅ Нет синтаксических ошибок')
        print()