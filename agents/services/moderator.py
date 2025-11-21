from typing import Dict, Any
from agents.base import BaseAgent

class ModeratorAgent(BaseAgent):
    """
    Agent designed to check content for safety and violations.
    """
    def __init__(self):
        super().__init__(agent_name="Moderator")

    def _get_system_prompt(self) -> str:
        return """You are a Content Moderator AI.
        Your job is to ensure all content on UnitySphere is safe, respectful, and appropriate.
        You strictly follow safety guidelines."""

    def check_content(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for potential violations.
        Returns JSON: {'is_safe': bool, 'reason': str, 'flagged_categories': list}
        """
        prompt = f"""
        Analyze the following text for hate speech, harassment, explicit content, or spam.
        Text: "{text}"
        
        Return a JSON object with:
        - 'is_safe': boolean
        - 'reason': string (explanation if unsafe, else "Safe")
        - 'flagged_categories': list of strings (e.g., ['hate_speech'])
        """
        
        return self.ask_llm_json(prompt)
