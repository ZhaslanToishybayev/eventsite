# 🚀 How to Transfer UnitySphere Project to VPS

## 📋 Prerequisites

Before transferring the project, ensure your VPS is ready:

### 1. VPS Setup Complete
Your VPS should have:
- ✅ Ubuntu 20.04/22.04 or CentOS 8/9
- ✅ Docker and Docker Compose installed
- ✅ UnitySphere user created (`unitysphere`)
- ✅ Nginx installed
- ✅ Firewall configured
- ✅ SSH access with sudo privileges

**Quick setup command:**
```bash
ssh root@your-vps-ip
curl -O https://raw.githubusercontent.com/your-repo/unitysphere/scripts/setup_vps.sh
chmod +x setup_vps.sh && ./setup_vps.sh
```

### 2. Domain Configuration
- ✅ Domain `fan-club.kz` points to your VPS IP
- ✅ DNS propagation completed

### 3. Production Configuration
- ✅ `.env.production` file created and configured
- ✅ OpenAI API key ready
- ✅ Google OAuth credentials ready

## 🚀 Method 1: Automated Transfer (Recommended)

### Step 1: Generate Production Secrets
```bash
cd /path/to/unitysphere
python3 scripts/generate_production_secrets.py > .env.production
```

### Step 2: Configure .env.production
Edit the file and fill in required values:
```bash
nano .env.production
```

Required values:
- `DJANGO_SECRET_KEY` (use generated)
- `POSTGRES_PASSWORD` (use generated)
- `OPENAI_API_KEY` (your OpenAI key)
- `GOOGLE_CLIENT_ID` (your Google OAuth)
- `GOOGLE_CLIENT_SECRET` (your Google OAuth)
- `ALLOWED_HOSTS=fan-club.kz,www.fan-club.kz`
- `CSRF_TRUSTED_ORIGINS=https://fan-club.kz,https://www.fan-club.kz`

### Step 3: Transfer Project
```bash
# Make script executable
chmod +x scripts/transfer_to_vps.sh

# Transfer to VPS
./scripts/transfer_to_vps.sh your-vps-ip 22 root
```

**Parameters:**
- `your-vps-ip` - Your VPS IP address
- `22` - SSH port (default: 22)
- `root` - SSH username (default: root)

### Step 4: Configure SSL
```bash
ssh root@your-vps-ip
sudo certbot --nginx -d fan-club.kz -d www.fan-club.kz
```

## 📦 Method 2: Manual Transfer

### Step 1: Archive Project Locally
```bash
cd /path/to/unitysphere

# Create archive
tar -czf unitysphere-project.tar.gz \
    manage.py \
    requirements.txt \
    requirements.production.txt \
    docker-compose.yaml \
    docker-compose.production.yaml \
    .env.production \
    scripts/ \
    nginx/ \
    core/ \
    accounts/ \
    clubs/ \
    agents/ \
    ai_consultant/ \
    api/ \
    static/ \
    templates/ \
    media/ \
    DEPLOYMENT_GUIDE.md \
    QUICK_START_PRODUCTION.md \
    PRODUCTION_DEPLOYMENT_CHECKLIST.md
```

### Step 2: Transfer Archive
```bash
scp -P 22 unitysphere-project.tar.gz root@your-vps-ip:/opt/
```

### Step 3: Extract and Setup on VPS
```bash
ssh root@your-vps-ip

# Extract archive
cd /opt
sudo tar -xzf unitysphere-project.tar.gz
sudo mv unitysphere-project unitysphere
sudo chown -R unitysphere:unitysphere unitysphere

# Set up environment
cd /opt/unitysphere
sudo cp .env.production .env
sudo chmod 600 .env
sudo chmod +x scripts/*.sh

# Create directories
sudo mkdir -p logs backups staticfiles media
sudo chown -R unitysphere:unitysphere .

# Deploy
sudo -u unitysphere bash scripts/deploy_production.sh
```

### Step 4: Configure SSL
```bash
sudo certbot --nginx -d fan-club.kz -d www.fan-club.kz
```

## 🔧 Method 3: Git-based Transfer

### Step 1: Set up Git Repository
```bash
# On your local machine
cd /path/to/unitysphere

# Initialize git if not already done
git init
git add .
git commit -m "Production ready"

# Add remote repository (GitHub, GitLab, etc.)
git remote add origin https://github.com/your-username/unitysphere.git
git push -u origin main
```

### Step 2: Clone on VPS
```bash
ssh root@your-vps-ip

# Install git if not present
apt-get update && apt-get install -y git

# Clone project
cd /opt
sudo git clone https://github.com/your-username/unitysphere.git unitysphere
sudo chown -R unitysphere:unitysphere unitysphere

# Configure environment
cd /opt/unitysphere
sudo cp .env.production.example .env.production
sudo nano .env.production  # Fill in values
sudo cp .env.production .env
sudo chmod 600 .env
sudo chmod +x scripts/*.sh

# Deploy
sudo -u unitysphere bash scripts/deploy_production.sh
```

## ✅ Verification Steps

After transfer, verify everything works:

### 1. Check Docker Containers
```bash
ssh root@your-vps-ip
docker-compose -f /opt/unitysphere/docker-compose.production.yaml ps
```

Expected output:
```
NAME                     COMMAND                  STATUS
unitysphere-fnclub       "gunicorn core.wsgi:…"   Up 3 seconds
unitysphere-fnclub-db    "docker-entrypoint.s…"   Up 4 seconds
unitysphere-fnclub-redis "docker-entrypoint.s…"   Up 5 seconds
```

### 2. Check Service Status
```bash
sudo systemctl status unitysphere
```

### 3. Test Health Endpoint
```bash
curl https://fan-club.kz/api/v1/ai/health/
```

Expected response:
```json
{
  "overall_status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "ai_api": "healthy"
  }
}
```

### 4. Test Main Page
```bash
curl -I https://fan-club.kz/
```

Expected: HTTP 200 OK

## 🛠️ Post-Transfer Setup

### 1. Configure Monitoring
```bash
ssh root@your-vps-ip
sudo bash /opt/unitysphere/scripts/setup_monitoring.sh
```

### 2. Set up Systemd Service
```bash
sudo bash /opt/unitysphere/scripts/setup_systemd_service.sh
```

### 3. Create Superuser (if not done during deploy)
```bash
sudo -u unitysphere docker-compose -f /opt/unitysphere/docker-compose.production.yaml exec -T fnclub python manage.py createsuperuser
```

### 4. Configure Django Site
```bash
sudo -u unitysphere docker-compose -f /opt/unitysphere/docker-compose.production.yaml exec -T fnclub python manage.py shell
```

In Django shell:
```python
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = 'fan-club.kz'
site.name = 'UnitySphere Fan Club'
site.save()
exit()
```

## 📚 Management Commands

After transfer, use these commands for management:

```bash
# Check service status
sudo systemctl status unitysphere

# View logs
sudo docker-compose -f /opt/unitysphere/docker-compose.production.yaml logs -f

# Health check
/usr/local/bin/unitysphere-health-check

# Backup database
/usr/local/bin/unitysphere-backup

# Restart service
/usr/local/bin/unitysphere-restart

# Deploy updates
cd /opt/unitysphere
sudo -u unitysphere git pull origin main
sudo -u unitysphere bash scripts/deploy_production.sh
```

## 🚨 Troubleshooting

### Connection Issues
```bash
# Test SSH connection
ssh -p 22 root@your-vps-ip

# Check if port is open
telnet your-vps-ip 22
```

### Permission Issues
```bash
# Fix permissions
sudo chown -R unitysphere:unitysphere /opt/unitysphere
sudo chmod 600 /opt/unitysphere/.env
```

### Docker Issues
```bash
# Check Docker status
sudo systemctl status docker

# Check Docker images
docker images

# Check Docker system
docker system df
```

### Nginx Issues
```bash
# Check Nginx status
sudo systemctl status nginx

# Test Nginx config
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

## 🎉 Success!

Your UnitySphere project is now transferred to VPS and ready for production use at `https://fan-club.kz`!

**Next steps:**
1. Monitor logs for the first 24 hours
2. Test all functionality (user registration, AI consultant, etc.)
3. Set up external monitoring (UptimeRobot, etc.)
4. Configure backup strategy
5. Optimize performance based on usage patterns