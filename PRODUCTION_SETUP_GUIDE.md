# UnitySphere Production Setup Guide

## Prerequisites

- Docker and Docker Compose installed
- Domain name configured (e.g., fan-club.kz)
- SSL certificate (Let's Encrypt recommended)
- Google OAuth credentials
- OpenAI API key

---

## Step 1: Environment Configuration

### 1.1 Update `.env` file

```bash
# Django Configuration
DJANGO_SECRET_KEY=<generate-new-secret-key>
DEBUG=False

# Database Configuration
POSTGRES_NAME=unitysphere_prod
POSTGRES_USER=unitysphere_user
POSTGRES_PASSWORD=<strong-password>
POSTGRES_HOST=fnclub-db
POSTGRES_PORT=5432

# OpenAI Configuration
OPENAI_API_KEY=<your-production-openai-key>
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7

# AI Consultant Settings
AI_CONSULTANT_ENABLED=True
AI_CONSULTANT_MAX_HISTORY_MESSAGES=10
AI_CONSULTANT_MAX_SESSIONS_PER_USER=50

# Google OAuth (get from Google Cloud Console)
GOOGLE_CLIENT_ID=<your-client-id>
GOOGLE_CLIENT_SECRET=<your-client-secret>
```

### 1.2 Generate Django Secret Key

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

---

## Step 2: Update Django Settings for Production

Edit `core/settings.py`:

```python
# Set DEBUG to False
DEBUG = False

# Update ALLOWED_HOSTS
ALLOWED_HOSTS = ['fan-club.kz', 'www.fan-club.kz', 'your-ip-address']

# Update CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = [
    'https://fan-club.kz',
    'https://www.fan-club.kz',
]
```

---

## Step 3: Google OAuth Setup

### 3.1 Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Google+ API"

### 3.2 Create OAuth Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Application type: "Web application"
4. Authorized JavaScript origins:
   - `https://fan-club.kz`
   - `https://www.fan-club.kz`
5. Authorized redirect URIs:
   - `https://fan-club.kz/accounts/google/login/callback/`
   - `https://www.fan-club.kz/accounts/google/login/callback/`

### 3.3 Configure in Django
After deployment, run:

```bash
docker compose exec fnclub python manage.py shell

# In Django shell:
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

site = Site.objects.get(id=1)
site.domain = 'fan-club.kz'
site.name = 'UnitySphere'
site.save()

google_app = SocialApp.objects.get(provider='google')
google_app.client_id = 'YOUR_CLIENT_ID'
google_app.secret = 'YOUR_CLIENT_SECRET'
google_app.save()
google_app.sites.add(site)
```

---

## Step 4: Database Backup Strategy

### 4.1 Create Backup Script

Create `scripts/backup_db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/unitysphere_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

docker compose exec -T fnclub-db pg_dump -U postgres postgres > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

### 4.2 Setup Cron Job

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/scripts/backup_db.sh
```

---

## Step 5: Nginx Configuration

Create `/etc/nginx/sites-available/unitysphere`:

```nginx
upstream unitysphere {
    server localhost:8001;
}

server {
    listen 80;
    server_name fan-club.kz www.fan-club.kz;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name fan-club.kz www.fan-club.kz;

    ssl_certificate /etc/letsencrypt/live/fan-club.kz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/fan-club.kz/privkey.pem;

    client_max_body_size 100M;

    location / {
        proxy_pass http://unitysphere;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/unitysphere/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /path/to/unitysphere/media/;
        expires 30d;
    }
}
```

Enable site:
```bash
ln -s /etc/nginx/sites-available/unitysphere /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

---

## Step 6: SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d fan-club.kz -d www.fan-club.kz

# Auto-renewal is set up automatically
# Test renewal:
sudo certbot renew --dry-run
```

---

## Step 7: Deploy Application

### 7.1 Build and Start Containers

```bash
cd /path/to/unitysphere
docker compose build
docker compose up -d
```

### 7.2 Run Migrations

```bash
docker compose exec fnclub python /proj/manage.py migrate
```

### 7.3 Collect Static Files

```bash
docker compose exec fnclub python /proj/manage.py collectstatic --noinput
```

### 7.4 Create Superuser

```bash
docker compose exec fnclub python /proj/manage.py createsuperuser
```

---

## Step 8: Post-Deployment Verification

### 8.1 Health Check

```bash
curl https://fan-club.kz/api/v1/ai/health/
```

Expected response:
```json
{
  "overall_status": "healthy",
  "components": {
    "database": "healthy",
    "cache": "healthy",
    "ai_service": "healthy"
  }
}
```

### 8.2 Test AI Consultant

```bash
# Create session
SESSION=$(curl -X POST -H "Content-Type: application/json" \
    https://fan-club.kz/api/v1/ai/chat/session/ | jq -r .id)

# Send message
curl -X POST -H "Content-Type: application/json" \
    -d "{\"session_id\": \"$SESSION\", \"message\": \"Привет\"}" \
    https://fan-club.kz/api/v1/ai/chat/message/
```

### 8.3 Test Google OAuth

1. Open `https://fan-club.kz/accounts/google/login/`
2. Should redirect to Google login
3. After authentication, should create user and login

---

## Step 9: Monitoring & Logging

### 9.1 View Logs

```bash
# Application logs
docker compose logs -f fnclub

# Database logs
docker compose logs -f fnclub-db

# Last 100 lines
docker compose logs --tail=100 fnclub
```

### 9.2 Setup Log Rotation

Create `/etc/logrotate.d/unitysphere`:

```
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    missingok
    delaycompress
    copytruncate
}
```

### 9.3 Monitoring Recommendations

- **Uptime Monitoring:** UptimeRobot, Pingdom
- **Error Tracking:** Sentry
- **Performance Monitoring:** New Relic, DataDog
- **Log Management:** ELK Stack, Papertrail

---

## Step 10: Maintenance Tasks

### Daily
- Monitor error logs
- Check disk space
- Verify backup completion

### Weekly
- Review AI API usage and costs
- Check system performance metrics
- Review user feedback

### Monthly
- Update dependencies (security patches)
- Review and optimize database queries
- Analyze user engagement metrics

---

## Troubleshooting

### Issue: Container won't start
```bash
docker compose logs fnclub
docker compose restart fnclub
```

### Issue: Database connection errors
```bash
docker compose exec fnclub-db psql -U postgres -d postgres
# Check if database is accessible
```

### Issue: Static files not loading
```bash
docker compose exec fnclub python /proj/manage.py collectstatic --noinput
```

### Issue: OpenAI API errors
- Check API key is valid
- Verify API usage limits not exceeded
- Check network connectivity

---

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `DJANGO_SECRET_KEY` set
- [ ] Strong database password
- [ ] SSL certificate configured
- [ ] Real Google OAuth credentials (not dummy)
- [ ] Firewall configured (only 80, 443 open)
- [ ] Database backups automated
- [ ] Regular security updates
- [ ] API rate limiting configured
- [ ] CORS settings reviewed

---

## Support & Documentation

- **Django Documentation:** https://docs.djangoproject.com/
- **Docker Documentation:** https://docs.docker.com/
- **OpenAI API:** https://platform.openai.com/docs
- **Google OAuth:** https://developers.google.com/identity

---

**Last Updated:** 2025-11-21
