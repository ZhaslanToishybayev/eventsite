import pytest
from django.test import TestCase
from ..agents.specialists.club_agent import ClubAgent
from ..agents.specialists.support_agent import SupportAgent
from ..agents.specialists.mentor_agent import MentorAgent
from ..agents.specialists.orchestrator import OrchestratorAgent

class TestAgents(TestCase):
    def test_club_agent_properties(self):
        agent = ClubAgent()
        self.assertEqual(agent.name, "club_specialist")
        self.assertTrue("club" in agent.description.lower())
        
        tools = agent.get_tools()
        self.assertTrue(len(tools) > 0)
        self.assertEqual(tools[0]['function']['name'], 'search_clubs')

    def test_support_agent_properties(self):
        agent = SupportAgent()
        self.assertEqual(agent.name, "support_specialist")
        self.assertTrue("support" in agent.description.lower())
        
        tools = agent.get_tools()
        self.assertTrue(len(tools) > 0)
        self.assertEqual(tools[0]['function']['name'], 'get_platform_status')

    def test_mentor_agent_properties(self):
        agent = MentorAgent()
        self.assertEqual(agent.name, "mentor_specialist")
        self.assertTrue("development" in agent.description.lower())
        
        tools = agent.get_tools()
        self.assertTrue(len(tools) > 0)
        # Check for one of the tools
        tool_names = [t['function']['name'] for t in tools]
        self.assertIn('get_development_recommendations', tool_names)

    def test_orchestrator_agent_properties(self):
        agent = OrchestratorAgent()
        self.assertEqual(agent.name, "orchestrator")
        
        # Orchestrator might not have tools
        tools = agent.get_tools()
        self.assertEqual(len(tools), 0)

    def test_system_prompts(self):
        club_agent = ClubAgent()
        support_agent = SupportAgent()
        
        club_prompt = club_agent.get_system_prompt()
        support_prompt = support_agent.get_system_prompt()
        
        self.assertIn("Club Specialist", club_prompt)
        self.assertIn("Support Specialist", support_prompt)
