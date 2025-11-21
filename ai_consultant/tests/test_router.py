import pytest
from unittest.mock import Mock, patch
from django.test import TestCase
from ..agents.router import AgentRouter
from ..agents.registry import AgentRegistry
from ..agents.specialists.club_agent import ClubAgent
from ..agents.specialists.support_agent import SupportAgent
from ..agents.specialists.orchestrator import OrchestratorAgent
from ..agents.specialists.mentor_agent import MentorAgent

class TestAgentRouter(TestCase):
    def setUp(self):
        self.openai_service = Mock()
        self.router = AgentRouter(self.openai_service)

    def test_route_to_club_agent(self):
        # Mock OpenAI response for club intent
        self.openai_service.chat_completion.return_value = {
            'content': '{"agent": "club_specialist", "reason": "User wants to find a club"}'
        }
        
        agent = self.router.route("I want to find a chess club", [])
        self.assertEqual(agent, "club_specialist")

    def test_route_to_support_agent(self):
        # Mock OpenAI response for support intent
        self.openai_service.chat_completion.return_value = {
            'content': '{"agent": "support_specialist", "reason": "User has a technical issue"}'
        }
        
        agent = self.router.route("My login is not working", [])
        self.assertEqual(agent, "support_specialist")

    def test_route_to_mentor_agent(self):
        # Mock OpenAI response for mentor intent
        self.openai_service.chat_completion.return_value = {
            'content': '{"agent": "mentor_specialist", "reason": "User wants to learn python"}'
        }
        
        agent = self.router.route("I want to learn Python", [])
        self.assertEqual(agent, "mentor_specialist")




    def test_fallback_to_orchestrator_on_error(self):
        # Mock OpenAI error
        self.openai_service.chat_completion.side_effect = Exception("API Error")
        
        agent = self.router.route("Hello", [])
        self.assertEqual(agent, "orchestrator")

    def test_fallback_to_orchestrator_on_invalid_json(self):
        # Mock invalid JSON response
        self.openai_service.chat_completion.return_value = {
            'content': 'Not JSON'
        }
        
        agent = self.router.route("Hello", [])
        self.assertEqual(agent, "orchestrator")

    def test_fallback_to_orchestrator_on_unknown_agent(self):
        # Mock unknown agent response
        self.openai_service.chat_completion.return_value = {
            'content': '{"agent": "unknown_agent"}'
        }
        
        agent = self.router.route("Hello", [])
        self.assertEqual(agent, "orchestrator")
