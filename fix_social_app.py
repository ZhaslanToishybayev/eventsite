#!/usr/bin/env python3
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, '/var/www/myapp/eventsite')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Setup Django
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# Get or create fan-club.kz site
site, created = Site.objects.get_or_create(
    domain='fan-club.kz',
    defaults={'name': 'fan-club.kz'}
)

if created:
    print(f'✅ Created new site: {site.domain}')
else:
    print(f'✅ Found existing site: {site.domain}')

# Update Google SocialApp
try:
    google_app = SocialApp.objects.get(provider='google')
    google_app.sites.clear()
    google_app.sites.add(site)
    google_app.save()
    print(f'✅ Updated Google SocialApp to use site: {site.domain}')
except SocialApp.DoesNotExist:
    print('❌ Google SocialApp not found')

print('')
print('✅ Google OAuth fix applied!')
print('📝 Make sure these redirect URIs are configured in Google Cloud Console:')
print('   • https://fan-club.kz/accounts/google/login/callback/')
print('   • https://www.fan-club.kz/accounts/google/login/callback/')