#!/bin/bash

# Скрипт для запуска всех MCP серверов
echo "🚀 Запуск MCP серверов для Claude Code..."

# Создаем директорию для логов
mkdir -p logs

# Запуск Serena AI MCP сервера (если еще не запущен)
if ! pgrep -f "serena start-mcp-server" > /dev/null; then
    echo "🤖 Запуск Serena AI MCP сервера..."
    export PATH="$HOME/.local/bin:$PATH"
    uvx --from git+https://github.com/oraios/serena serena start-mcp-server \
        --project . \
        --transport streamable-http \
        --port 8001 \
        > logs/serena_mcp.log 2>&1 &
    echo "Serena AI запущен на порту 8001"
else
    echo "✅ Serena AI уже запущен"
fi

# Запуск файловой системы MCP сервера
echo "📁 Запуск файловой системы MCP сервера..."
npx @modelcontextprotocol/server-filesystem \
    /home/zhaslan/Downloads/unitysphere-project/home/almalinux/new/unitysphere \
    > logs/filesystem_mcp.log 2>&1 &

# Запуск MCP сервера для выполнения кода
echo "⚡ Запуск Code Runner MCP сервера..."
npx mcp-server-code-runner --transport stdio > logs/code_runner_mcp.log 2>&1 &

# Запуск Chrome DevTools MCP сервера
echo "🌐 Запуск Chrome DevTools MCP сервера..."
npx chrome-devtools-mcp > logs/chrome_devtools_mcp.log 2>&1 &

# Запуск веб-исследовательского MCP сервера
echo "🔍 Запуск Web Research MCP сервера..."
npx @mzxrai/mcp-webresearch > logs/web_research_mcp.log 2>&1 &

echo ""
echo "✅ Все MCP серверы запущены!"
echo "📋 Логи доступны в директории logs/"
echo ""
echo "🔧 Доступные MCP серверы:"
echo "  - Serena AI (порт 8001) - анализ кода"
echo "  - Filesystem - работа с файлами"
echo "  - Code Runner - выполнение кода"
echo "  - Chrome DevTools - отладка браузера"
echo "  - Web Research - веб-исследования"
echo ""
echo "⏹️  Для остановки используйте: ./stop_mcp_servers.sh"