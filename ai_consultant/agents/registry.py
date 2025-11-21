"""
📚 Agent Registry
Manages the registration and retrieval of AI agents.
"""

from typing import Dict, Type, Optional
from .base import BaseAgent

class AgentRegistry:
    _registry: Dict[str, Type[BaseAgent]] = {}

    @classmethod
    def register(cls, agent_class: Type[BaseAgent]):
        """Decorator to register an agent"""
        cls._registry[agent_class.name] = agent_class
        return agent_class

    @classmethod
    def get_agent(cls, name: str) -> Optional[Type[BaseAgent]]:
        """Get an agent class by name"""
        return cls._registry.get(name)

    @classmethod
    def get_all_agents(cls) -> Dict[str, Type[BaseAgent]]:
        """Get all registered agents"""
        return cls._registry.copy()
