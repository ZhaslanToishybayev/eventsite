"""
End-to-End Test for AI Agent Tool Execution
Tests that the Club Agent can create clubs and events through the full pipeline.
"""
import os
import django
import sys
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

# Setup Django
sys.path.append('/home/zhaslan/Downloads/unitysphere-project/home/almalinux/new/unitysphere')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from ai_consultant.services_v2 import AIConsultantServiceV2
from ai_consultant.models import ChatSession
from clubs.models import Club, ClubCategory, ClubEvent

User = get_user_model()

def test_create_club_via_agent():
    """Test creating a club through the AI agent"""
    print("\n🧪 Test 1: Create Club via Agent")
    print("=" * 60)
    
    # Create test user
    user, _ = User.objects.get_or_create(
        email='test_agent@example.com',
        defaults={'phone': '+77771234567'}
    )
    
    # Create session
    session = ChatSession.objects.create(user=user)
    
    # Mock OpenAI to return a tool call
    mock_openai_response = {
        'choices': [{
            'message': {
                'role': 'assistant',
                'content': None,
                'tool_calls': [{
                    'id': 'call_123',
                    'type': 'function',
                    'function': {
                        'name': 'create_club',
                        'arguments': '{"name": "Test Chess Club", "description": "A club for chess enthusiasts in Almaty", "category": "Хобби", "city": "Almaty"}'
                    }
                }]
            },
            'finish_reason': 'tool_calls'
        }],
        'usage': {'total_tokens': 100}
    }
    
    with patch('ai_consultant.services.openai_client.OpenAIClientService.chat_completion') as mock_chat:
        mock_chat.return_value = mock_openai_response
        
        # Create AI service
        ai_service = AIConsultantServiceV2()
        
        # Send message
        message = "I want to create a chess club called 'Test Chess Club' in Almaty for hobby enthusiasts"
        
        try:
            result = ai_service.send_message(session, message)
            print(f"✅ Agent processed message")
            print(f"   Response: {result.get('response', 'No response')[:100]}...")
            
            # Check if club was created
            club = Club.objects.filter(name="Test Chess Club").first()
            if club:
                print(f"✅ Club created successfully!")
                print(f"   ID: {club.id}")
                print(f"   Name: {club.name}")
                print(f"   Category: {club.category.name if club.category else 'None'}")
                club.delete()  # Cleanup
            else:
                print(f"⚠️ Club was not created (tool might not have been executed)")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    
    # Cleanup - delete club first if it exists
    Club.objects.filter(name="Test Chess Club").delete()
    session.delete()
    user.delete()

def test_create_event_via_agent():
    """Test creating an event through the AI agent"""
    print("\n🧪 Test 2: Create Event via Agent")
    print("=" * 60)
    
    # Create test user and club
    user, _ = User.objects.get_or_create(
        email='test_event@example.com',
        defaults={'phone': '+77771234568'}
    )
    
    category, _ = ClubCategory.objects.get_or_create(
        name='Спорт',
        defaults={'is_active': True}
    )
    
    club = Club.objects.create(
        name='Test Sports Club',
        category=category,
        creater=user,
        description='Test club for events'
    )
    
    session = ChatSession.objects.create(user=user)
    
    # Mock OpenAI to return event creation tool call
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d 10:00')
    tomorrow_end = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d 12:00')
    
    mock_openai_response = {
        'choices': [{
            'message': {
                'role': 'assistant',
                'content': None,
                'tool_calls': [{
                    'id': 'call_456',
                    'type': 'function',
                    'function': {
                        'name': 'create_event',
                        'arguments': f'{{"club_id": "{club.id}", "title": "Test Tournament", "description": "A friendly tournament", "start_datetime": "{tomorrow}", "end_datetime": "{tomorrow_end}", "location": "Central Park"}}'
                    }
                }]
            },
            'finish_reason': 'tool_calls'
        }],
        'usage': {'total_tokens': 100}
    }
    
    with patch('ai_consultant.services.openai_client.OpenAIClientService.chat_completion') as mock_chat:
        mock_chat.return_value = mock_openai_response
        
        ai_service = AIConsultantServiceV2()
        
        message = f"Create a tournament event for my club tomorrow at 10 AM"
        
        try:
            result = ai_service.send_message(session, message)
            print(f"✅ Agent processed message")
            print(f"   Response: {result.get('response', 'No response')[:100]}...")
            
            # Check if event was created
            event = ClubEvent.objects.filter(title="Test Tournament", club=club).first()
            if event:
                print(f"✅ Event created successfully!")
                print(f"   ID: {event.id}")
                print(f"   Title: {event.title}")
                print(f"   Location: {event.location}")
                print(f"   Start: {event.start_datetime}")
                event.delete()  # Cleanup
            else:
                print(f"⚠️ Event was not created (tool might not have been executed)")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Cleanup
    session.delete()
    club.delete()
    user.delete()

def main():
    print("\n" + "=" * 60)
    print("🚀 AI AGENT END-TO-END TESTING")
    print("=" * 60)
    print("\nThis test verifies that AI agents can execute tools")
    print("(create_club, create_event) through the full pipeline.\n")
    
    test_create_club_via_agent()
    test_create_event_via_agent()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()
