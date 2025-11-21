"""
🎓 Mentor Specialist Agent
Provides professional development guidance, learning recommendations, and career advice.
"""

from typing import Dict, Any, List
from ..base import BaseAgent
from ..registry import AgentRegistry
from ...prompts.enhanced_agent_prompts import PromptFactory

@AgentRegistry.register
class MentorAgent(BaseAgent):
    name = "mentor_specialist"
    description = "Expert in professional development, learning paths, skills, and career growth"

    def get_system_prompt(self, user_context: Dict[str, Any] = None) -> str:
        """Получить улучшенный промпт из фабрики промптов"""
        return PromptFactory.get_prompt('mentor_specialist')

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_development_recommendations",
                    "description": "Get personalized development recommendations based on user's goals and interests",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "User's development goals or areas of interest"
                            },
                            "current_level": {
                                "type": "string",
                                "description": "Current skill level: beginner, intermediate, advanced",
                                "enum": ["beginner", "intermediate", "advanced"]
                            },
                            "category": {
                                "type": "string",
                                "description": "Area of development: professional, creative, communication, personal",
                                "enum": ["professional", "creative", "communication", "personal"]
                            }
                        },
                        "required": ["message"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_my_progress",
                    "description": "Get user's current progress on active development plans and achievements",
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
                    "name": "start_development_path",
                    "description": "Enroll user in a specific development path or learning program",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path_id": {
                                "type": "string",
                                "description": "ID of the development path to start"
                            },
                            "goal": {
                                "type": "string",
                                "description": "User's specific goal for this path"
                            }
                        },
                        "required": ["path_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_clubs_for_development",
                    "description": "Search for clubs that help with specific skill development",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "skill": {
                                "type": "string",
                                "description": "Skill to develop (e.g., 'leadership', 'programming', 'public speaking')"
                            },
                            "category": {
                                "type": "string",
                                "description": "Club category preference",
                                "enum": ["sport", "hobby", "profession"]
                            },
                            "level": {
                                "type": "string",
                                "description": "Skill level",
                                "enum": ["beginner", "intermediate", "advanced"]
                            }
                        },
                        "required": ["skill"]
                    }
                }
            }
        ]