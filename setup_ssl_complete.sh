#!/bin/bash
# 🚀 Complete SSL Setup and nginx Configuration Script
# Creates SSL certificates and configures nginx for HTTPS

echo "🔐 Setting up complete SSL solution for fan-club.kz"
echo "=================================================="

# Create SSL directory
echo "📁 Creating SSL certificate directory..."
sudo mkdir -p /etc/ssl/fan-club.kz
sudo mkdir -p /etc/letsencrypt/live/fan-club.kz

# Generate SSL certificate for fan-club.kz
echo "🔐 Generating SSL certificate for fan-club.kz..."

# Method 1: Try to get certificate from Let's Encrypt (if domain points to this server)
if command -v certbot &> /dev/null; then
    echo "📋 Attempting to get certificate from Let's Encrypt..."
    sudo certbot certonly --standalone -d fan-club.kz --agree-tos --email admin@fan-club.kz || {
        echo "❌ Let's Encrypt failed, generating self-signed certificate..."
        # Generate self-signed certificate
        sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /etc/ssl/fan-club.kz/fan-club.kz.key \
            -out /etc/ssl/fan-club.kz/fan-club.kz.crt \
            -subj "/CN=fan-club.kz/O=Fan Club/C=KZ" || {
                echo "❌ Failed to generate certificate, using snakeoil..."
                sudo cp /etc/ssl/certs/ssl-cert-snakeoil.pem /etc/ssl/fan-club.kz/fan-club.kz.crt 2>/dev/null || true
                sudo cp /etc/ssl/private/ssl-cert-snakeoil.key /etc/ssl/fan-club.kz/fan-club.kz.key 2>/dev/null || true
            }
    }
else
    echo "📋 Let's Encrypt not available, generating self-signed certificate..."
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/ssl/fan-club.kz/fan-club.kz.key \
        -out /etc/ssl/fan-club.kz/fan-club.kz.crt \
        -subj "/CN=fan-club.kz/O=Fan Club/C=KZ" || {
        echo "❌ Failed to generate certificate, using snakeoil..."
        sudo cp /etc/ssl/certs/ssl-cert-snakeoil.pem /etc/ssl/fan-club.kz/fan-club.kz.crt 2>/dev/null || true
        sudo cp /etc/ssl/private/ssl-cert-snakeoil.key /etc/ssl/fan-club.kz/fan-club.kz.key 2>/dev/null || true
    }
fi

# Create symlinks for Let's Encrypt compatibility
echo "🔗 Creating certificate symlinks..."
sudo ln -sf /etc/ssl/fan-club.kz/fan-club.kz.crt /etc/letsencrypt/live/fan-club.kz/fullchain.pem 2>/dev/null || true
sudo ln -sf /etc/ssl/fan-club.kz/fan-club.kz.key /etc/letsencrypt/live/fan-club.kz/privkey.pem 2>/dev/null || true

# Set proper permissions
echo "🔒 Setting proper certificate permissions..."
sudo chmod 644 /etc/ssl/fan-club.kz/fan-club.kz.crt
sudo chmod 600 /etc/ssl/fan-club.kz/fan-club.kz.key
sudo chmod 644 /etc/letsencrypt/live/fan-club.kz/fullchain.pem 2>/dev/null || true
sudo chmod 600 /etc/letsencrypt/live/fan-club.kz/privkey.pem 2>/dev/null || true

# Verify certificates exist
if [ -f /etc/ssl/fan-club.kz/fan-club.kz.crt ] && [ -f /etc/ssl/fan-club.kz/fan-club.kz.key ]; then
    echo "✅ SSL certificates generated successfully!"
    echo "   Certificate: /etc/ssl/fan-club.kz/fan-club.kz.crt"
    echo "   Private Key: /etc/ssl/fan-club.kz/fan-club.kz.key"
else
    echo "❌ SSL certificate generation failed!"
    exit 1
fi

echo ""
echo "⚙️  Creating nginx configuration with SSL support..."