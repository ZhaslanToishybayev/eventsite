from typing import List, Dict, Any
from agents.base import BaseAgent
from clubs.models import Club

class ClubManagerAgent(BaseAgent):
    """
    Agent designed to assist club owners with management tasks.
    """
    def __init__(self):
        super().__init__(agent_name="ClubManager")

    def _get_system_prompt(self) -> str:
        return """You are an expert Club Manager AI. 
        Your goal is to help community leaders grow their clubs, increase engagement, and organize events.
        You are creative, practical, and encouraging."""

    def suggest_events(self, club: Club) -> List[Dict[str, Any]]:
        """
        Generate event ideas based on the club's category and description.
        """
        prompt = f"""
        Suggest 3 engaging event ideas for a club named "{club.name}".
        Category: {club.category.name}
        Description: {club.description}
        
        Return the result as a JSON list of objects with keys: 'title', 'description', 'estimated_cost', 'difficulty'.
        """
        
        response = self.ask_llm_json(prompt)
        if isinstance(response, list):
            return response
        elif isinstance(response, dict) and 'events' in response:
            return response['events']
        return []

    def draft_announcement(self, club: Club, topic: str) -> str:
        """
        Draft a text announcement for the club.
        """
        prompt = f"""
        Write a short, exciting announcement for the club "{club.name}" about: {topic}.
        Use emojis and keep it under 200 words.
        """
        return self.ask_llm(prompt)
