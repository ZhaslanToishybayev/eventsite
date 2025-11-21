"""
🤖 Base Agent Class
Abstract base class for all AI agents in the system.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from django.conf import settings

class BaseAgent(ABC):
    """
    Abstract base class for AI agents.
    Each agent has a specific role, tools, and system prompt.
    """
    
    def __init__(self, context_service=None):
        self.context_service = context_service
        self.model = "gpt-4-turbo-preview"  # Default model, can be overridden

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the agent"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this agent does"""
        pass

    @abstractmethod
    def get_system_prompt(self, user_context: Dict[str, Any] = None) -> str:
        """Returns the system prompt for this agent"""
        pass

    def get_tools(self) -> List[Dict[str, Any]]:
        """Returns a list of OpenAI tools (functions) available to this agent"""
        return []

    def process_message(self, message: str, history: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        Process a user message and return a response.
        Can be overridden for custom logic, but default implementation
        should handle standard chat flow with tools.
        """
        # This method will be implemented in the concrete classes or 
        # handled by the main ChatService using the agent's properties.
        pass
