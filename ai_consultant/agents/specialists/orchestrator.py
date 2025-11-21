"""
🎼 Orchestrator Agent
The generalist agent that handles greetings and unclear intents.
"""

from typing import Dict, Any
from ..base import BaseAgent
from ..registry import AgentRegistry
from ...prompts.enhanced_agent_prompts import PromptFactory

@AgentRegistry.register
class OrchestratorAgent(BaseAgent):
    name = "orchestrator"
    description = "Generalist agent for greetings and fallback"

    def get_system_prompt(self, user_context: Dict[str, Any] = None) -> str:
        """Получить улучшенный промпт из фабрики промптов"""
        return PromptFactory.get_prompt('orchestrator')
