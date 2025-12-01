# 🚀 UnitySphere Production Launch Commands

## ⚡ **QUICK PRODUCTION LAUNCH**

**UnitySphere Enhanced AI Club Creation System** готов к production запуску!

## 📋 **IMMEDIATE STEPS (Requires sudo):**

### **1. Configure nginx (1 minute):**
```bash
sudo cp /var/www/myapp/eventsite/nginx_production.conf /etc/nginx/sites-available/unitysphere
sudo ln -sf /etc/nginx/sites-available/unitysphere /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
```

### **2. Setup SSL (Optional, 2 minutes):**
```bash
# Если есть SSL сертификаты:
sudo cp /path/to/cert.pem /etc/letsencrypt/live/fan-club.kz/fullchain.pem
sudo cp /path/to/private.key /etc/letsencrypt/live/fan-club.kz/privkey.pem
sudo chmod 644 /etc/letsencrypt/live/fan-club.kz/fullchain.pem
sudo chmod 600 /etc/letsencrypt/live/fan-club.kz/privkey.pem
sudo systemctl restart nginx
```

### **3. Create systemd service (2 minutes):**
```bash
sudo cat > /etc/systemd/system/unitysphere.service << 'EOF'
[Unit]
Description=UnitySphere Django Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/myapp/eventsite
Environment="PATH=/var/www/myapp/eventsite/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=core.settings"
ExecStart=/var/www/myapp/eventsite/venv/bin/gunicorn --workers 3 --worker-class gthread --threads 2 --bind 127.0.0.1:8001 --timeout 120 --keep-alive 5 --max-requests 1000 --max-requests-jitter 50 core.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable unitysphere
sudo systemctl start unitysphere
```

### **4. Configure firewall (30 seconds):**
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

## 🧪 **TEST PRODUCTION:**

### **Verify deployment:**
```bash
curl -I http://fan-club.kz/
curl http://fan-club.kz/api/v1/ai/health/
curl -I http://fan-club.kz/static/css/
```

**Expected:** HTTP 200 responses

## 🎯 **PRODUCTION URLS:**

- **🌐 Main Site**: http://fan-club.kz
- **🔒 HTTPS**: https://fan-club.kz (after SSL setup)
- **🤖 AI API**: http://fan-club.kz/api/v1/ai/club-creation/agent/
- **⚙️ Admin**: http://fan-club.kz/admin/

## 📊 **SYSTEM STATUS:**

✅ **Django Backend**: Running on port 8001
✅ **AI Agent**: Fully functional
✅ **ALLOWED_HOSTS**: Configured for fan-club.kz
✅ **Database**: Active with real data
✅ **Static Files**: Ready
⚠️ **nginx**: Needs configuration (see commands above)

## 🚨 **IF NGINX NOT AVAILABLE:**

**Django server is running on port 8001:**
```bash
# Direct access:
curl http://127.0.0.1:8001/
curl http://127.0.0.1:8001/api/v1/ai/health/
```

**Use direct IP:port until nginx configured.**

## 🎉 **READY FOR PRODUCTION!**

**UnitySphere Enhanced AI Club Creation System** будет полностью работать после выполнения nginx настройки!

**Ключевые возможности:**
- 🤖 AI агент для создания клубов
- 📊 Реальная статистика (420+ клубов)
- 💬 Natural Russian conversation
- 📱 Mobile responsive design
- ✅ Production-ready architecture

**🚀 Сайт будет доступен по адресу: fan-club.kz**