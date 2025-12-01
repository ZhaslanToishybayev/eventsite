#!/usr/bin/env python3
"""
Simple Django test to verify the application is working
"""

import os
import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    import django
    django.setup()

    from django.test.client import Client
    from django.http import HttpResponse

    print("✅ Django setup successful")

    # Test basic functionality
    client = Client()
    response = client.get('/')
    print(f"✅ Main page response: {response.status_code}")

    # Test API endpoint
    api_response = client.get('/api/v1/ai/club-creation/guide/')
    print(f"✅ API endpoint response: {api_response.status_code}")

    if api_response.status_code == 200:
        print("🎉 Django application is working correctly!")
        print("🌐 Ready to serve requests through nginx")
    else:
        print(f"⚠️ API endpoint returned: {api_response.status_code}")

except Exception as e:
    print(f"❌ Django setup failed: {e}")
    import traceback
    traceback.print_exc()