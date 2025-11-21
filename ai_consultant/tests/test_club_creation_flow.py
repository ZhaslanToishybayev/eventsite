import json
from django.test import TestCase
from django.contrib.auth import get_user_model

from ai_consultant.services.chat import ChatService

User = get_user_model()

class FakeOpenAI:
    def chat_completion(self, messages, tools=None, tool_choice=None):
        # Not used in intercepted state-machine flow
        return {"success": True, "content": "OK", "tokens_used": 1}

class FakeClubCreationService:
    def create_club(self, user, name, description, category, city, is_private=False):
        assert name and description and category
        return {
            'success': True,
            'club_id': '123',
            'club_name': name,
            'link': f'/clubs/123/'
        }

class FakeServiceProvider:
    def __init__(self):
        self.club_creation_service = FakeClubCreationService()
        # Minimal stubs for other services used by tools executor
        self.club_management_service = type('X', (), {})()
        self.development_service = type('Y', (), {})()
        self.knowledge_service = type('Z', (), {'search': lambda self, q: [], 'format_results': lambda self, r: '[]'})()
        self.platform_service_manager = type('P', (), {})()

class ClubCreationFlowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.chat = ChatService(openai_service=FakeOpenAI(), service_provider=FakeServiceProvider())
        self.session = self.chat.create_session(self.user)

    def send(self, text):
        return self.chat.send_message(self.session, text)

    def test_full_creation_flow_with_corrections(self):
        # Start intent
        r1 = self.send("Хочу создать клуб")
        self.assertIn('Шаг 1', r1['response'])

        # Name
        r2 = self.send("Шахматный клуб Алматы")
        self.assertIn('Шаг 2', r2['response'])

        # Too short description
        r3 = self.send("Коротко")
        self.assertIn('минимум 200', r3['response'])

        # Proper long description
        long_desc = 'A'*210
        r4 = self.send(long_desc)
        self.assertIn('Шаг 3', r4['response'])

        # Category
        r5 = self.send("Спорт")
        self.assertIn('Шаг 4', r5['response'])

        # City
        r6 = self.send("Алматы")
        self.assertIn('Проверь данные', r6['response'])

        # Correction request
        r7 = self.send("Нет, хочу изменить категорию")
        self.assertIn('категорию', r7['response'].lower())

        # New category
        r8 = self.send("IT")
        self.assertIn('город', r8['response'].lower()) or self.assertIn('проверь', r8['response'].lower())

        # Confirm
        r9 = self.send("Да")
        self.assertIn('успешно', r9['response'].lower())
        self.assertEqual(r9['agent'], 'club_specialist')
        self.assertIn('club_id', r9)
