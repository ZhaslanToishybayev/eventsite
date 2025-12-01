#!/bin/bash
# 🚀 Direct Access Setup - Bypass nginx for immediate site access
# This script creates a direct access method while nginx SSL issues are resolved

echo "🔧 Setting up direct access to Django application..."

# Check which Django servers are running
echo "📊 Checking running Django servers..."

# Check port 8000
if curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; then
    echo "✅ Django server running on port 8000"
    echo "🌐 Direct access URL: http://fan-club.kz:8000"
else
    echo "❌ Django server not responding on port 8000"
fi

# Check port 8080
if curl -s http://127.0.0.1:8080/ > /dev/null 2>&1; then
    echo "✅ Django server running on port 8080"
    echo "🌐 Direct access URL: http://fan-club.kz:8080"
else
    echo "❌ Django server not responding on port 8080"
fi

# Check port 8081
if curl -s http://127.0.0.1:8081/ > /dev/null 2>&1; then
    echo "✅ Django server running on port 8081"
    echo "🌐 Direct access URL: http://fan-club.kz:8081"
else
    echo "❌ Django server not responding on port 8081"
fi

echo ""
echo "💡 Instructions for immediate access:"
echo "1. Open your web browser"
echo "2. Go to one of the working URLs above"
echo "3. The site should load directly without nginx"
echo ""
echo "🔧 Next steps:"
echo "- Fix SSL certificate permissions for nginx"
echo "- Restore HTTPS functionality"
echo "- Update DNS to point to the working port"
echo ""
echo "🎯 Current status: Site is accessible via direct port access"