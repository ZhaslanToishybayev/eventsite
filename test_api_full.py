import os
import django
import json
from unittest.mock import patch, MagicMock

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse

User = get_user_model()

# Allow testserver host
from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS += ['testserver']

def test_api_endpoints():
    print("🌐 Starting API Endpoint Verification...")
    print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    
    client = APIClient()
    
    # Create test user
    user, _ = User.objects.get_or_create(
        email='api_test_user@example.com', 
        defaults={
            'first_name': 'API', 
            'last_name': 'Tester',
            'phone': '+77009998877'
        }
    )
    client.force_authenticate(user=user)
    print(f"   User authenticated: {user.email}")

    # Mock the AI Service
    with patch('ai_consultant.api.views.AIConsultantServiceV2') as MockService:
        mock_instance = MockService.return_value
        
        # 1. Test Welcome Message
        print("\n1. Testing /api/ai/welcome/...")
        try:
            url = reverse('ai_consultant_api:welcome_message')
            response = client.get(url)
            if response.status_code == 200:
                print("   ✅ Welcome message: OK")
            else:
                print(f"   ❌ Welcome message Failed: {response.status_code}")
        except Exception as e:
             print(f"   ❌ Exception: {e}")

        # 2. Test Create Session
        print("\n2. Testing /api/ai/sessions/create/...")
        import uuid
        valid_uuid = str(uuid.uuid4())
        mock_instance.create_chat_session.return_value = MagicMock(id=valid_uuid)
        try:
            url = reverse('ai_consultant_api:create_chat_session')
            response = client.post(url)
            if response.status_code == 201:
                print("   ✅ Create Session: OK")
                session_id = response.data.get('id')
            else:
                print(f"   ❌ Create Session Failed: {response.status_code}")
                session_id = valid_uuid # Fallback
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            session_id = valid_uuid

        # 3. Test Chat (Advanced)
        print("\n3. Testing /api/ai/chat-advanced/...")
        # Mock chat_business_service.process_message
        with patch('ai_consultant.api.views.chat_business_service') as mock_chat_biz:
            mock_chat_biz.process_message.return_value = ({'response': 'Hello from API test'}, 200)
            
            try:
                url = reverse('ai_consultant_api:chat_advanced')
                data = {'message': 'Hello API', 'session_id': session_id}
                response = client.post(url, data, format='json')
                
                if response.status_code == 200:
                    print("   ✅ Chat Advanced: OK")
                else:
                    print(f"   ❌ Chat Advanced Failed: {response.status_code}")
                    print(f"      Response: {response.data}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")

        # 4. Test Club Recommendations
        print("\n4. Testing /api/ai/recommendations/clubs/...")
        mock_instance.get_club_recommendations_for_user.return_value = {'recommendations': []}
        try:
            url = reverse('ai_consultant_api:club_recommendations')
            response = client.get(url)
            if response.status_code == 200:
                print("   ✅ Club Recommendations: OK")
            else:
                print(f"   ❌ Club Recommendations Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

        # 5. Test Feedback
        print("\n5. Testing /api/ai/feedback/...")
        # Patch the service where it is defined, as it might be imported locally or we missed the import
        with patch('ai_consultant.services.feedback.FeedbackService') as MockFeedback:
            MockFeedback.return_value.create_feedback.return_value = {'success': True}
            try:
                url = reverse('ai_consultant_api:create_feedback')
                data = {'message': 'Great app!', 'category': 'general'}
                response = client.post(url, data, format='json')
                if response.status_code == 201:
                    print("   ✅ Create Feedback: OK")
                else:
                    print(f"   ❌ Create Feedback Failed: {response.status_code}")
                    print(f"      Response: {response.data}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")

    print("\n✅ API Verification Complete!")

if __name__ == "__main__":
    test_api_endpoints()
