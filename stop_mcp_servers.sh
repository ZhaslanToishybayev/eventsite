#!/bin/bash

# Скрипт для остановки всех MCP серверов
echo "🛑 Остановка MCP серверов..."

# Остановка Serena AI
pkill -f "serena start-mcp-server" 2>/dev/null && echo "✅ Serena AI остановлен"

# Остановка файловой системы MCP сервера
pkill -f "@modelcontextprotocol/server-filesystem" 2>/dev/null && echo "✅ Filesystem MCP сервер остановлен"

# Остановка Code Runner MCP сервера
pkill -f "mcp-server-code-runner" 2>/dev/null && echo "✅ Code Runner MCP сервер остановлен"

# Остановка Chrome DevTools MCP сервера
pkill -f "chrome-devtools-mcp" 2>/dev/null && echo "✅ Chrome DevTools MCP сервер остановлен"

# Остановка Web Research MCP сервера
pkill -f "@mzxrai/mcp-webresearch" 2>/dev/null && echo "✅ Web Research MCP сервер остановлен"

echo ""
echo "🎯 Все MCP серверы остановлены!"