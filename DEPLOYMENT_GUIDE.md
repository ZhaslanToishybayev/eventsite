# 🚀 Production Deployment Guide for UnitySphere (fan-club.kz)

## 📋 Overview

This guide will help you deploy UnitySphere to your VPS and configure it to run on the domain `fan-club.kz`.

## 🎯 Prerequisites

### Server Requirements
- **OS**: Ubuntu 20.04/22.04 or CentOS 8/9
- **CPU**: 2+ cores
- **RAM**: 2+ GB
- **Disk**: 20+ GB free space
- **Network**: Public IP address
- **Domain**: `fan-club.kz` pointing to your server IP

### Before Starting
- [ ] VPS server is ready and accessible
- [ ] Domain DNS is configured to point to server IP
- [ ] You have root access to the server
- [ ] OpenAI API key is ready
- [ ] Google OAuth credentials are prepared (optional)

## 🔧 Step 1: Server Preparation

### 1.1 Connect to your VPS
```bash
ssh root@your-vps-ip
```

### 1.2 Run the automated setup script
```bash
# Download the setup script
curl -O https://raw.githubusercontent.com/your-repo/unitysphere/scripts/setup_vps.sh
chmod +x setup_vps.sh
./setup_vps.sh
```

This script will:
- Install system packages (nginx, docker, git, etc.)
- Configure firewall and security
- Create necessary users and directories
- Set up monitoring and backup scripts

## 🔐 Step 2: Generate Production Secrets

### 2.1 Generate secure keys
```bash
cd /opt/unitysphere
python3 scripts/generate_production_secrets.py > production_secrets.env
```

### 2.2 Create .env.production file
```bash
cp .env.production.example .env.production
nano .env.production
```

### 2.3 Fill in the required values:
```bash
# Django Configuration
DJANGO_SECRET_KEY=your-generated-secret-key
DEBUG=False

# Database Configuration
POSTGRES_PASSWORD=your-secure-postgres-password

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Google OAuth (optional for now)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Domain Configuration
ALLOWED_HOSTS=fan-club.kz,www.fan-club.kz
CSRF_TRUSTED_ORIGINS=https://fan-club.kz,https://www.fan-club.kz

# Email Configuration
RESEND_API_KEY=your-resend-api-key
```

### 2.4 Set proper permissions
```bash
chmod 600 .env.production
chown unitysphere:unitysphere .env.production
```

## 📦 Step 3: Deploy Application

### 3.1 Copy project files
```bash
# From your local machine
scp -r . unitysphere@your-vps-ip:/opt/unitysphere/
```

### 3.2 Deploy using the deployment script
```bash
sudo -u unitysphere bash scripts/deploy_production.sh
```

This script will:
- Build Docker images
- Set up the database
- Apply migrations
- Collect static files
- Create superuser (you'll be prompted)
- Configure Google OAuth
- Set up SSL certificates

## 🌐 Step 4: Configure Nginx and SSL

### 4.1 Copy Nginx configuration
```bash
sudo cp nginx/fan-club.kz.conf /etc/nginx/sites-available/unitysphere
sudo ln -sf /etc/nginx/sites-available/unitysphere /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
```

### 4.2 Test and reload Nginx
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 4.3 Get SSL certificate
```bash
sudo certbot --nginx -d fan-club.kz -d www.fan-club.kz
```

### 4.4 Set up automatic renewal
```bash
echo "0 2 * * 0 /usr/bin/certbot renew --quiet" | sudo crontab -
```

## 🔧 Step 5: Final Configuration

### 5.1 Create superuser (if not done during deployment)
```bash
sudo -u unitysphere docker-compose -f docker-compose.production.yaml exec -T fnclub python manage.py createsuperuser
```

### 5.2 Configure Django Site
```bash
sudo -u unitysphere docker-compose -f docker-compose.production.yaml exec -T fnclub python manage.py shell
```

In the Django shell:
```python
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = 'fan-club.kz'
site.name = 'UnitySphere Fan Club'
site.save()
exit()
```

### 5.3 Set up systemd service for autostart
```bash
sudo systemctl enable unitysphere
sudo systemctl start unitysphere
```

## ✅ Step 6: Verification

### 6.1 Check services status
```bash
sudo docker-compose -f docker-compose.production.yaml ps
sudo systemctl status nginx
sudo systemctl status unitysphere
```

### 6.2 Run health checks
```bash
curl -I https://fan-club.kz/
curl https://fan-club.kz/api/v1/ai/health/
```

### 6.3 Test functionality
- [ ] Main page loads correctly
- [ ] Admin panel accessible: `https://fan-club.kz/admin/`
- [ ] AI consultant responds: `https://fan-club.kz/api/v1/ai/chat/`
- [ ] Google OAuth works: `https://fan-club.kz/accounts/google/login/`
- [ ] Static files load (CSS, JS, images)

## 🔍 Monitoring and Maintenance

### Health Monitoring
```bash
# Check application health
/usr/local/bin/unitysphere-health-check

# View logs
sudo docker-compose -f docker-compose.production.yaml logs --tail=100 fnclub
sudo tail -f /var/log/unitysphere/django.log
```

### Backups
```bash
# Manual backup
/usr/local/bin/unitysphere-backup

# Check backup status
ls -la /backups/unitysphere/
```

### Updates
```bash
# Pull latest changes and redeploy
sudo -u unitysphere git pull origin main
sudo -u unitysphere bash scripts/deploy_production.sh
```

## 🚨 Troubleshooting

### Common Issues

**1. Site not loading**
```bash
# Check nginx status
sudo systemctl status nginx
sudo nginx -t

# Check firewall
sudo ufw status
```

**2. Database connection errors**
```bash
# Check database container
sudo docker-compose -f docker-compose.production.yaml logs fnclub-db

# Restart database
sudo docker-compose -f docker-compose.production.yaml restart fnclub-db
```

**3. SSL certificate issues**
```bash
# Renew certificate
sudo certbot renew --force-renewal

# Check certificate
sudo certbot certificates
```

**4. Permission issues**
```bash
# Fix permissions
sudo chown -R unitysphere:unitysphere /opt/unitysphere
sudo chmod 600 /opt/unitysphere/.env.production
```

### Log Locations
- Application logs: `/var/log/unitysphere/django.log`
- AI logs: `/var/log/unitysphere/ai.log`
- Nginx logs: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- Docker logs: `docker-compose logs fnclub`

### Emergency Procedures

**Rollback deployment:**
```bash
# Stop current services
sudo systemctl stop unitysphere
sudo docker-compose -f docker-compose.production.yaml down

# Restore from backup
sudo docker-compose -f docker-compose.production.yaml exec -T fnclub-db psql -U postgres -c "DROP DATABASE unitysphere;"
sudo docker-compose -f docker-compose.production.yaml exec -T fnclub-db psql -U postgres -c "CREATE DATABASE unitysphere;"
sudo docker-compose -f docker-compose.production.yaml exec -T fnclub-db bash -c "gunzip -c /backups/backup_date/database.sql.gz | psql -U postgres"

# Restart services
sudo systemctl start unitysphere
```

## 📞 Support

If you encounter issues:

1. **Check logs first**: Look at application and system logs
2. **Health checks**: Run the health check script
3. **Docker status**: Verify all containers are running
4. **Network connectivity**: Ensure domain resolves correctly
5. **Resource usage**: Check CPU, memory, and disk usage

## 🎉 Success!

Your UnitySphere application should now be running on `https://fan-club.kz` with:
- ✅ SSL encryption
- ✅ Production database (PostgreSQL)
- ✅ Redis caching
- ✅ Nginx reverse proxy
- ✅ Docker containerization
- ✅ Automated backups
- ✅ Health monitoring
- ✅ Security hardening

The application is ready for production use!