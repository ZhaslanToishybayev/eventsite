#!/bin/bash

echo "🔧 Fixing 502 Bad Gateway error..."

# Stop current nginx
echo "🛑 Stopping nginx..."
sudo systemctl stop nginx

# Backup current config
echo "💾 Backing up current config..."
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# Copy temporary config without SSL
echo "📋 Applying temporary config without SSL..."
sudo cp /tmp/nginx_temp.conf /etc/nginx/nginx.conf

# Test configuration
echo "✅ Testing nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "🎉 Configuration test passed! Starting nginx..."
    sudo systemctl start nginx

    # Check if nginx started successfully
    if sudo systemctl is-active --quiet nginx; then
        echo "✅ Nginx started successfully!"
        echo "🌐 Website should now be accessible at: http://fan-club.kz"
        echo ""
        echo "📝 Next steps:"
        echo "1. Test website access: curl -I http://fan-club.kz"
        echo "2. Set up proper SSL certificates with certbot"
        echo "3. Configure production server (gunicorn + systemd)"
    else
        echo "❌ Failed to start nginx. Checking logs..."
        sudo systemctl status nginx
    fi
else
    echo "❌ Configuration test failed. Restoring backup..."
    sudo cp /etc/nginx/nginx.conf.backup /etc/nginx/nginx.conf
fi