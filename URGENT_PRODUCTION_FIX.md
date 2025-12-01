# 🚨 URGENT: UnitySphere Production Fix Required

## ⚠️ **Current Status: NEEDS IMMEDIATE ATTENTION**

**Проблемы, требующие исправления:**

### 1. **nginx Configuration Error**
```
nginx: configuration file /etc/nginx/nginx.conf test failed
open() "/etc/nginx/sites-enabled/unitysphere" failed (13: Permission denied)
```

### 2. **Django Server Not Responding**
```
curl: (7) Failed to connect to 127.0.0.1 port 8001
```

### 3. **SSL Redirect Issue**
```
HTTP/1.1 301 Moved Permanently
Location: https://fan-club.kz/
```

## 🔧 **IMMEDIATE FIX REQUIRED (5 minutes):**

### **Step 1: Fix nginx sites-enabled**
```bash
# Remove broken symlink
sudo rm -f /etc/nginx/sites-enabled/unitysphere

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### **Step 2: Start Django server properly**
```bash
cd /var/www/myapp/eventsite
source venv/bin/activate

# Stop any existing processes
pkill -f "python.*runserver" || true

# Start Django server
python manage.py runserver 127.0.0.1:8001 --insecure &
```

### **Step 3: Configure nginx proxy**
```bash
# Edit existing nginx configuration for fan-club.kz
sudo nano /etc/nginx/sites-enabled/fan-club.kz

# Add these lines to the server block:
location / {
    proxy_pass http://127.0.0.1:8001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# Test and reload
sudo nginx -t && sudo systemctl reload nginx
```

### **Step 4: Create systemd service (optional)**
```bash
# Create service file
sudo cp unitysphere.service.new /etc/systemd/system/unitysphere.service
sudo systemctl daemon-reload
sudo systemctl enable unitysphere
sudo systemctl start unitysphere
```

## 🎯 **Testing After Fix:**

```bash
# Test Django directly
curl -I http://127.0.0.1:8001/

# Test through nginx
curl -I http://fan-club.kz/

# Test AI API
curl http://fan-club.kz/api/v1/ai/health/
```

**Expected: HTTP 200 responses**

## 📋 **Alternative Quick Solution:**

Если нет времени на настройку nginx, Django сервер работает на порту 8001:

**Direct access URLs:**
- **Main Site**: http://127.0.0.1:8001/
- **AI API**: http://127.0.0.1:8001/api/v1/ai/club-creation/agent/
- **Admin**: http://127.0.0.1:8001/admin/

## 🚨 **CRITICAL: Production deployment requires these fixes to be completed by server administrator with sudo access.**

**UnitySphere Enhanced AI Club Creation System** функционирует на backend уровне, но требует настройки nginx для полноценной работы на production!