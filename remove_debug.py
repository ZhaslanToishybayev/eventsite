#!/usr/bin/env python3
"""
Удаление DEBUG сообщений из production кода
"""

import re

def remove_debug_statements():
    """Удаляем все DEBUG print() из кода"""

    file_path = "/var/www/myapp/eventsite/simplified_interactive_ai.py"

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Удаляем все строки с DEBUG print()
    lines = content.split('\n')
    filtered_lines = []

    for line in lines:
        # Удаляем строки с DEBUG print
        if 'print(f"DEBUG:' in line:
            continue
        # Удаляем standalone DEBUG print
        if 'print("DEBUG:' in line:
            continue
        # Сохраняем остальные строки
        filtered_lines.append(line)

    new_content = '\n'.join(filtered_lines)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("✅ DEBUG сообщения удалены из кода")

if __name__ == "__main__":
    remove_debug_statements()