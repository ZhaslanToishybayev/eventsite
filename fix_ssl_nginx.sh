#!/bin/bash
# 🚀 Quick Fix for SSL Certificate Issues
# This script temporarily disables HTTPS to restore site functionality

echo "🔧 Fixing SSL certificate issues..."

# Stop nginx
echo "🛑 Stopping nginx..."
sudo systemctl stop nginx

# Backup current nginx config
echo "💾 Backing up current nginx config..."
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.ssl_backup

# Replace with HTTP-only config
echo "📋 Replacing with HTTP-only configuration..."
sudo cp /var/www/myapp/eventsite/nginx_temp.conf /etc/nginx/nginx.conf

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration test passed!"

    # Start nginx
    echo "🚀 Starting nginx..."
    sudo systemctl start nginx

    # Check nginx status
    echo "📊 Checking nginx status..."
    sudo systemctl status nginx --no-pager -l

    # Test site accessibility
    echo "🌐 Testing site accessibility..."
    sleep 3
    curl -I http://127.0.0.1:80/ 2>/dev/null | head -1

    echo ""
    echo "🎉 SUCCESS: Site should now be accessible via HTTP!"
    echo "📝 Note: SSL certificates need to be fixed for HTTPS access"
    echo "🔗 Site URL: http://fan-club.kz"
else
    echo "❌ Nginx configuration test failed!"
    echo "🔄 Restoring original configuration..."
    sudo cp /etc/nginx/nginx.conf.ssl_backup /etc/nginx/nginx.conf
    sudo systemctl start nginx
fi