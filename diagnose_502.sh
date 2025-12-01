#!/bin/bash
# 🔍 Comprehensive 502 Error Diagnostic Script

echo "🔍 Diagnosing 502 Bad Gateway Error..."
echo "=========================================="

# Check if nginx is running
echo "1. Checking nginx service status..."
if systemctl is-active --quiet nginx 2>/dev/null; then
    echo "   ✅ nginx is running"
else
    echo "   ❌ nginx is not running"
    echo "   🔧 Try: sudo systemctl start nginx"
fi

# Check nginx configuration
echo ""
echo "2. Testing nginx configuration..."
if nginx -t 2>/dev/null; then
    echo "   ✅ nginx configuration is valid"
else
    echo "   ❌ nginx configuration has errors"
fi

# Check if Django server is running on expected port
echo ""
echo "3. Checking Django backend server..."
if curl -s http://127.0.0.1:8080/ > /dev/null 2>&1; then
    echo "   ✅ Django server responding on port 8080"
else
    echo "   ❌ Django server not responding on port 8080"
    echo "   🔧 Django servers available:"
    for port in 8000 8001 8080 8081; do
        if curl -s http://127.0.0.1:$port/ > /dev/null 2>&1; then
            echo "      ✅ Port $port is working"
        else
            echo "      ❌ Port $port is not responding"
        fi
    done
fi

# Check nginx error log for specific issues
echo ""
echo "4. Checking nginx error logs..."
if [ -f /var/log/nginx/error.log ]; then
    echo "   Last 5 error log entries:"
    tail -5 /var/log/nginx/error.log 2>/dev/null | head -5
else
    echo "   ❌ Cannot access nginx error log"
fi

# Check if SSL certificate files exist and are readable
echo ""
echo "5. Checking SSL certificate files..."
if [ -f /etc/letsencrypt/live/fan-club.kz/fullchain.pem ]; then
    echo "   ✅ SSL certificate file exists"
    if [ -r /etc/letsencrypt/live/fan-club.kz/fullchain.pem ]; then
        echo "   ✅ SSL certificate file is readable"
    else
        echo "   ❌ SSL certificate file is not readable"
        echo "   🔧 Fix: sudo chmod 644 /etc/letsencrypt/live/fan-club.kz/fullchain.pem"
    fi
else
    echo "   ❌ SSL certificate file does not exist"
fi

if [ -f /etc/letsencrypt/live/fan-club.kz/privkey.pem ]; then
    echo "   ✅ SSL private key exists"
    if [ -r /etc/letsencrypt/live/fan-club.kz/privkey.pem ]; then
        echo "   ✅ SSL private key is readable"
    else
        echo "   ❌ SSL private key is not readable"
        echo "   🔧 Fix: sudo chmod 644 /etc/letsencrypt/live/fan-club.kz/privkey.pem"
    fi
else
    echo "   ❌ SSL private key does not exist"
fi

# Check nginx upstream configuration
echo ""
echo "6. Checking nginx upstream configuration..."
echo "   Expected Django backend: 127.0.0.1:8080"
echo "   🔧 If Django is running on different port, update nginx config"

# Provide immediate solutions
echo ""
echo "🚨 IMMEDIATE SOLUTIONS:"
echo "======================"

echo ""
echo "Option 1: Restart services"
echo "   sudo systemctl restart nginx"
echo "   sudo systemctl restart gunicorn  # if using gunicorn"

echo ""
echo "Option 2: Check Django server status"
echo "   ps aux | grep 'python.*manage.py runserver'"
echo "   # If no Django server running, start one:"
echo "   cd /var/www/myapp/eventsite"
echo "   source venv/bin/activate"
echo "   python manage.py runserver 127.0.0.1:8080 --insecure &"

echo ""
echo "Option 3: Test direct access (bypass nginx)"
echo "   curl http://127.0.0.1:8080/"
echo "   # If this works, the issue is nginx configuration"

echo ""
echo "Option 4: Check firewall"
echo "   sudo ufw status"
echo "   # Ensure ports 80, 443, and 8080 are open"

echo ""
echo "🎯 CURRENT STATUS SUMMARY:"
echo "=========================="
echo "• nginx configuration: $(nginx -t 2>/dev/null && echo 'VALID' || echo 'INVALID')"
echo "• Django server: $(curl -s http://127.0.0.1:8080/ > /dev/null 2>&1 && echo 'WORKING' || echo 'NOT WORKING')"
echo "• SSL certificates: $(ls -la /etc/letsencrypt/live/fan-club.kz/ 2>/dev/null && echo 'EXISTS' || echo 'MISSING')"

echo ""
echo "💡 For immediate site access while fixing nginx:"
echo "   http://fan-club.kz:8000  (Django direct)"
echo "   http://fan-club.kz:8080  (Django direct)"