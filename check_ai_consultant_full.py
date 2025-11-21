import os
import django
import sys
from unittest.mock import MagicMock, patch

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from ai_consultant.services_v2 import AIConsultantServiceV2
from ai_consultant.models import ChatSession, ChatMessage

User = get_user_model()

def test_ai_consultant_full():
    print("Starting AI Consultant Full Verification...")
    
    # Mock OpenAI service to avoid actual API calls and costs/errors if key is missing
    with patch('ai_consultant.services.openai_client.OpenAIClientService') as MockOpenAI:
        # Setup mock response
        mock_instance = MockOpenAI.return_value
        mock_instance.chat_completion.return_value = {
            'success': True,
            'content': 'This is a mocked response from the AI consultant.',
            'tokens_used': 10,
            'tool_calls': None
        }
        mock_instance.is_available.return_value = True

        try:
            # 1. Initialize Service
            print("\n1. Initializing AIConsultantServiceV2...")
            service = AIConsultantServiceV2()
            print("   Service initialized successfully.")

            # 2. Health Check
            print("\n2. Running Health Check...")
            health = service.health_check()
            print(f"   Health Check Result: {health}")
            if health['status'] != 'healthy':
                print("   WARNING: Health check reported issues.")

            # 3. Create User and Session
            print("\n3. Creating Test User and Session...")
            # Check if User model has username field
            try:
                user, created = User.objects.get_or_create(email='test_ai@example.com', defaults={'first_name': 'Test', 'last_name': 'User'})
                if created:
                    user.set_password('testpass123')
                    user.save()
            except Exception as e:
                print(f"   Error creating user: {e}")
                # Fallback if username is required but we don't know it (unlikely given the error)
                user = User.objects.first()
                print(f"   Using existing user: {user}")
            
            session = service.create_chat_session(user)
            print(f"   Session created: {session.id}")

            # 4. Send Message
            print("\n4. Sending Message...")
            user_message = "Hello, how can you help me?"
            response = service.send_message(session, user_message)
            print(f"   User Message: {user_message}")
            print(f"   AI Response: {response.get('response')}")
            
            if response.get('error'):
                print("   ERROR: Failed to get response from AI.")
            else:
                print("   Message sent and response received successfully.")

            # 5. Check History
            print("\n5. Checking Chat History...")
            history = service.get_chat_history(session)
            print(f"   History length: {len(history)}")
            if len(history) >= 2:
                print("   History verification passed (User message + AI response).")
            else:
                print("   WARNING: History length is unexpected.")

            # 6. Test Context Service
            print("\n6. Testing Context Service...")
            system_context = service.context_service.get_system_context()
            print(f"   System Context length: {len(system_context)}")
            
            # 7. Test Club Recommendations (Mocked)
            print("\n7. Testing Club Recommendations...")
            # We might need to mock recommendation service if it relies on external APIs or complex DB state
            # For now, let's try calling it and see if it crashes
            try:
                recs = service.get_club_recommendations_for_user(user)
                print(f"   Recommendations result: {recs.get('success')}, type: {recs.get('type')}")
            except Exception as e:
                print(f"   Error getting recommendations: {e}")

            # Cleanup
            print("\nCleaning up test session...")
            service.delete_session(session)
            print("Test session deleted.")

            print("\n✅ AI Consultant Verification Complete!")

        except Exception as e:
            print(f"\n❌ Verification Failed with error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_ai_consultant_full()
