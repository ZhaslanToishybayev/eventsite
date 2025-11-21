import pytest
from django.test import TestCase
from ..agents.specialists.club_agent import ClubAgent
from ..agents.specialists.support_agent import SupportAgent
from ..agents.specialists.orchestrator import OrchestratorAgent

class TestResponseDesign(TestCase):
    """
    Tests to ensure AI responses meet design and UX standards.
    """
    
    def test_club_agent_prompt_design(self):
        """Verify Club Agent prompt encourages structured responses"""
        agent = ClubAgent()
        prompt = agent.get_system_prompt()
        
        # Check for key design elements in instructions
        self.assertIn("Club Specialist", prompt)
        # Should encourage asking questions
        self.assertIn("Ask", prompt) 
        
    def test_orchestrator_prompt_design(self):
        """Verify Orchestrator prompt encourages friendly tone"""
        agent = OrchestratorAgent()
        prompt = agent.get_system_prompt()
        
        # Check for tone instructions
        self.assertIn("friendly", prompt.lower())
        self.assertIn("emojis", prompt.lower())
        
    def test_response_formatting_rules(self):
        """
        This test simulates checking a response for formatting rules.
        In a real scenario, we would pass a mock response through a validator.
        """
        # Example of what we expect from the AI
        good_response = """
        👋 Hello! I can help you with that.
        
        Here are some clubs:
        1. ♟️ Chess Club
        2. 🏃 Running Club
        
        Would you like to join one?
        """
        
        # Validation logic (that we want to enforce via prompts/tests)
        has_emoji = any(char in good_response for char in "👋♟️🏃")
        self.assertTrue(has_emoji, "Response should contain emojis")
        
        has_list = "1." in good_response or "-" in good_response
        self.assertTrue(has_list, "Response should use lists for options")
