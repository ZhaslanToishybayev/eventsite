"""
🔧 Support Specialist Agent
Handles technical support, how-to questions, and platform guidance.
"""

from typing import Dict, Any, List
from ..base import BaseAgent
from ..registry import AgentRegistry
from ...prompts.enhanced_agent_prompts import PromptFactory

@AgentRegistry.register
class SupportAgent(BaseAgent):
    name = "support_specialist"
    description = "Expert on platform features, technical support, and how-to guides"

    def get_system_prompt(self, user_context: Dict[str, Any] = None) -> str:
        """Получить улучшенный промпт из фабрики промптов"""
        return PromptFactory.get_prompt('support_specialist')

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_platform_status",
                    "description": "Check if the platform is operational and get system status",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Search the knowledge base for articles and guides",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (e.g. 'password reset', 'create club')"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
