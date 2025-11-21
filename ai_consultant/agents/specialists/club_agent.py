"""
🏆 Club Specialist Agent
Handles club-related queries: search, recommendations, and community features.
"""

from typing import Dict, Any, List
from ..base import BaseAgent
from ..registry import AgentRegistry
from ...prompts.enhanced_agent_prompts import PromptFactory

@AgentRegistry.register
class ClubAgent(BaseAgent):
    name = "club_specialist"
    description = "Expert on clubs, communities, and social features"

    def get_system_prompt(self, user_context: Dict[str, Any] = None) -> str:
        """Получить улучшенный промпт из фабрики промптов"""
        return PromptFactory.get_prompt('club_specialist')

    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_clubs",
                    "description": "Search for clubs by category, keywords, or location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (e.g., 'chess', 'sports', 'programming')"
                            },
                            "category": {
                                "type": "string",
                                "description": "Club category from database",
                                "enum": ["Спорт", "Хобби", "Профессия", "IT"]
                            },
                            "city": {
                                "type": "string",
                                "description": "City to filter by"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_club",
                    "description": "Create a new club with provided details",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Club name (unique, max 100 characters)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Club description (min 200 characters)"
                            },
                            "category": {
                                "type": "string",
                                "description": "Club category from database",
                                "enum": ["Спорт", "Хобби", "Профессия", "IT"]
                            },
                            "city": {
                                "type": "string",
                                "description": "Club location city"
                            },
                            "email": {
                                "type": "string",
                                "description": "Club contact email"
                            },
                            "phone": {
                                "type": "string",
                                "description": "Club contact phone"
                            },
                            "is_private": {
                                "type": "boolean",
                                "description": "Whether club requires approval to join",
                                "default": False
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Club tags for search"
                            }
                        },
                        "required": ["name", "description", "category", "city", "email", "phone"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_my_clubs",
                    "description": "Get clubs managed by the current user",
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
                    "name": "update_club",
                    "description": "Update club information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "club_id": {
                                "type": "string",
                                "description": "Club ID to update"
                            },
                            "name": {
                                "type": "string",
                                "description": "New club name"
                            },
                            "description": {
                                "type": "string",
                                "description": "New club description"
                            },
                            "category": {
                                "type": "string",
                                "description": "New club category from database",
                                "enum": ["Спорт", "Хобби", "Профессия", "IT"]
                            }
                        },
                        "required": ["club_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_event",
                    "description": "Create an event for a club",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "club_id": {
                                "type": "string",
                                "description": "Club ID to create event for"
                            },
                            "title": {
                                "type": "string",
                                "description": "Event title"
                            },
                            "description": {
                                "type": "string",
                                "description": "Event description"
                            },
                            "start_time": {
                                "type": "string",
                                "description": "Event start time (ISO format)"
                            },
                            "end_time": {
                                "type": "string",
                                "description": "Event end time (ISO format)"
                            },
                            "location": {
                                "type": "string",
                                "description": "Event location"
                            },
                            "age_restriction": {
                                "type": "integer",
                                "description": "Minimum age requirement (optional)"
                            }
                        },
                        "required": ["club_id", "title", "description", "start_time", "end_time", "location"]
                    }
                }
            }
        ]