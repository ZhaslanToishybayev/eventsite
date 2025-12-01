#!/bin/bash
# 🚀 Fixed SSL Setup Script - Uses Let's Encrypt certificates

echo "🔐 Setting up SSL certificates with Let's Encrypt..."

# Check if Let's Encrypt certificates exist
if [ -f /etc/letsencrypt/live/fan-club.kz-0001/fullchain.pem ] && [ -f /etc/letsencrypt/live/fan-club.kz-0001/privkey.pem ]; then
    echo "✅ Let's Encrypt certificates found!"
    echo "   Certificate: /etc/letsencrypt/live/fan-club.kz-0001/fullchain.pem"
    echo "   Private Key: /etc/letsencrypt/live/fan-club.kz-0001/privkey.pem"

    # Create symlinks with correct names
    sudo mkdir -p /etc/letsencrypt/live/fan-club.kz
    sudo ln -sf /etc/letsencrypt/live/fan-club.kz-0001/fullchain.pem /etc/letsencrypt/live/fan-club.kz/fullchain.pem
    sudo ln -sf /etc/letsencrypt/live/fan-club.kz-0001/privkey.pem /etc/letsencrypt/live/fan-club.kz/privkey.pem

    # Set proper permissions
    sudo chmod 644 /etc/letsencrypt/live/fan-club.kz/fullchain.pem
    sudo chmod 600 /etc/letsencrypt/live/fan-club.kz/privkey.pem

    echo "✅ SSL certificates setup completed successfully!"
    exit 0
else
    echo "❌ Let's Encrypt certificates not found, generating self-signed..."
    # Generate self-signed as fallback
    sudo mkdir -p /etc/ssl/fan-club.kz
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/ssl/fan-club.kz/fan-club.kz.key \
        -out /etc/ssl/fan-club.kz/fan-club.kz.crt \
        -subj "/CN=fan-club.kz/O=Fan Club/C=KZ"

    # Set proper permissions
    sudo chmod 644 /etc/ssl/fan-club.kz/fan-club.kz.crt
    sudo chmod 600 /etc/ssl/fan-club.kz/fan-club.kz.key

    if [ -f /etc/ssl/fan-club.kz/fan-club.kz.crt ] && [ -f /etc/ssl/fan-club.kz/fan-club.kz.key ]; then
        echo "✅ Self-signed SSL certificates generated successfully!"
        exit 0
    else
        echo "❌ SSL certificate generation failed!"
        exit 1
    fi
fi