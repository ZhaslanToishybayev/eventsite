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

# Check Google SocialApp
apps = SocialApp.objects.filter(provider='google')
print('Google SocialApp Configuration:')
print('===============================')

if apps.exists():
    for app in apps:
        print(f'  Name: {app.name}')
        print(f'  Client ID: {app.client_id}')
        print(f'  Secret: {app.secret}')
        print(f'  Sites: {list(app.sites.all())}')
else:
    print('  No Google SocialApp found')

print('')
print('Expected redirect URIs:')
print('=======================')
print('  • https://fan-club.kz/accounts/google/login/callback/')
print('  • https://www.fan-club.kz/accounts/google/login/callback/')