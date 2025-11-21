from typing import List, Dict, Any
from agents.base import BaseAgent
from accounts.models import User
from clubs.models import Club

class UserCompanionAgent(BaseAgent):
    """
    Agent designed to assist users in finding clubs and navigating the platform.
    """
    def __init__(self):
        super().__init__(agent_name="UserCompanion")

    def _get_system_prompt(self) -> str:
        return """You are a friendly and helpful companion for UnitySphere users.
        Your goal is to help them find communities where they belong.
        You are empathetic, enthusiastic, and knowledgeable about the platform."""

    def recommend_clubs(self, user: User, user_interests: str) -> List[str]:
        """
        Recommend clubs based on user interests.
        Note: In a real production system, this would use a vector DB. 
        Here we use LLM to match keywords against a small set of candidate clubs or just generate search terms.
        """
        # For this implementation, we'll ask the LLM to generate search keywords based on interests,
        # then we could search the DB. Or we can feed it a list of top clubs.
        # Let's try a hybrid approach: Ask LLM to analyze interests and suggest categories.
        
        prompt = f"""
        The user is interested in: "{user_interests}".
        Suggest 5 specific keywords or categories to search for in our club database.
        Return as a JSON list of strings.
        """
        
        keywords = self.ask_llm_json(prompt)
        if isinstance(keywords, list):
            return keywords
        return []

    def chat(self, user_message: str, history: List[Dict[str, str]]) -> str:
        """
        General chat capability.
        """
        # Construct conversation history
        messages = [{"role": "system", "content": self._get_system_prompt()}]
        for msg in history:
            messages.append(msg)
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            content = response.choices[0].message.content
            self.log_action("chat", f"User: {user_message[:20]}...")
            return content
        except Exception as e:
            self.log_action("error", str(e))
            return "I'm having trouble connecting right now. Please try again later."
