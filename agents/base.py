import os
import json
from typing import Dict, Any, Optional
from django.conf import settings
from openai import OpenAI
from .models import AgentLog

class BaseAgent:
    """
    Base class for all agents in the system.
    Handles OpenAI client initialization, common logging, and error handling.
    """
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')

    def log_action(self, action: str, details: str = ""):
        """
        Log an action to the database.
        """
        AgentLog.objects.create(
            agent_name=self.agent_name,
            action=action,
            details=details
        )

    def _get_system_prompt(self) -> str:
        """
        Override this in subclasses to define the agent's persona.
        """
        return "You are a helpful assistant for the UnitySphere platform."

    def ask_llm(self, user_prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        """
        Send a prompt to the LLM and return the response text.
        """
        sys_prompt = system_prompt or self._get_system_prompt()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=1000
            )
            content = response.choices[0].message.content
            self.log_action("ask_llm", f"Prompt: {user_prompt[:50]}... Response: {content[:50]}...")
            return content
        except Exception as e:
            error_msg = f"LLM Error: {str(e)}"
            self.log_action("error", error_msg)
            return f"Error: {error_msg}"

    def ask_llm_json(self, user_prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Ask LLM and expect a JSON response.
        """
        sys_prompt = system_prompt or self._get_system_prompt()
        sys_prompt += "\nIMPORTANT: Return ONLY valid JSON."
        
        response_text = self.ask_llm(user_prompt, sys_prompt, temperature=0.3)
        
        try:
            # Clean up potential markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
                
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            self.log_action("error", f"Failed to parse JSON: {response_text}")
            return {"error": "Failed to parse JSON response"}
