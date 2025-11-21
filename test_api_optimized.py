import os
import django
import sys
import json
from unittest.mock import MagicMock, patch

# Setup Django environment
sys.path.append('/home/zhaslan/Downloads/unitysphere-project/home/almalinux/new/unitysphere')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from django.test import RequestFactory
from rest_framework.test import APIClient
from rest_framework import status

# Allow testserver host
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS += ['testserver']

def test_api_endpoints():
    print("🌐 Starting Optimized API Endpoint Verification...")
    
    client = APIClient()
    
    # Mock the services to avoid external calls and DB locks
    # We patch where the class is DEFINED or where it is IMPORTED.
    # Since FeedbackService might be imported inside the function or not at top level, 
    # it's safest to patch the source.
    with patch('ai_consultant.services_v2.AIConsultantServiceV2') as MockService, \
         patch('services.ai.chat_business_service.chat_business_service') as mock_chat_biz, \
         patch('ai_consultant.services.feedback.FeedbackService') as MockFeedback:
        
        # Setup Mock Service Instance
        mock_service_instance = MockService.return_value
        mock_service_instance.create_chat_session.return_value = MagicMock(id='12345678-1234-5678-1234-567812345678')
        mock_service_instance.send_message.return_value = {
            'response': 'Hello from Mock AI',
            'message_id': 1
        }
        mock_service_instance.get_club_recommendations_for_user.return_value = []
        
        # Setup Mock Chat Business Service
        mock_chat_biz.process_message.return_value = ({'response': 'Biz Logic Response'}, 200)
        
        # Setup Mock Feedback Service
        mock_feedback_instance = MockFeedback.return_value
        mock_feedback_instance.create_feedback.return_value = {'success': True}

        # 1. Test Welcome Message
        print("\n🔹 Testing /api/v1/ai/welcome/...")
        try:
            response = client.get('/api/v1/ai/welcome/')
            if response.status_code == 200:
                print("   ✅ Success (200 OK)")
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.content}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

        # 2. Test Create Session
        print("\n🔹 Testing /api/v1/ai/sessions/create/...")
        try:
            response = client.post('/api/v1/ai/sessions/create/', {}, format='json')
            if response.status_code == 201:
                print("   ✅ Success (201 Created)")
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.content}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

        # 3. Test Chat (Advanced/V2)
        print("\n🔹 Testing /api/v1/ai/chat-advanced/ (POST)...")
        try:
            response = client.post('/api/v1/ai/chat-advanced/', {'message': 'Hello'}, format='json')
            if response.status_code == 200:
                print("   ✅ Success (200 OK)")
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.content}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

        # 4. Test Recommendations
        print("\n🔹 Testing /api/v1/ai/recommendations/clubs/...")
        try:
            # Need to force authentication for this one usually, but let's see if it handles anonymous
            client.force_authenticate(user=None) 
            response = client.get('/api/v1/ai/recommendations/clubs/')
            # Expecting 401 or 403 if not authenticated, or 200 if allowed
            if response.status_code in [200, 401, 403]:
                print(f"   ✅ Response received ({response.status_code})")
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.content}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

        # 5. Test Feedback
        print("\n🔹 Testing /api/v1/ai/feedback/...")
        try:
            response = client.post('/api/v1/ai/feedback/', {'message': 'Great app!'}, format='json')
            if response.status_code == 201:
                print("   ✅ Success (201 Created)")
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.content}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    test_api_endpoints()
