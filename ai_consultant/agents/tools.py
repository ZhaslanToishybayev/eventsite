import logging
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ToolExecutor:
    """
    Executes tools called by AI agents.
    """
    
    def __init__(self, service_provider):
        self.service_provider = service_provider

    def execute(self, agent_name: str, tool_name: str, tool_args: Dict[str, Any], user) -> str:
        """
        Executes a tool and returns the result as a string.
        """
        logger.info(f"Executing tool {tool_name} for agent {agent_name} with args {tool_args}")
        
        try:
            if agent_name == 'club_specialist':
                return self._execute_club_tools(tool_name, tool_args, user)
            elif agent_name == 'support_specialist':
                return self._execute_support_tools(tool_name, tool_args, user)
            elif agent_name == 'mentor_specialist':
                return self._execute_mentor_tools(tool_name, tool_args, user)
            
            return f"Error: Unknown agent {agent_name}"
            
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return f"Error executing tool {tool_name}: {str(e)}"

    def _execute_club_tools(self, tool_name: str, args: Dict, user) -> str:
        if tool_name == 'search_clubs':
            query = args.get('query', '')
            limit = args.get('limit', 5)
            
            # Use the method from AIConsultantServiceV2 (service_provider)
            result = self.service_provider.get_clubs_by_interest_keywords(query, limit)
            return self.service_provider.format_club_recommendations(result)
            
        elif tool_name == 'create_club':
            name = args.get('name')
            description = args.get('description')
            category = args.get('category')
            city = args.get('city')
            is_private = args.get('is_private', False)
            
            result = self.service_provider.club_creation_service.create_club(
                user, name, description, category, city, is_private
            )
            
            if result['success']:
                from ai_consultant.services.club_validator import ClubCreationConfirmation
                
                # Generate success message with next steps
                success_msg = ClubCreationConfirmation.generate_success_message(
                    result['club_name'],
                    result['club_id'],
                    result['link']
                )
                
                # Add suggestions if any
                if result.get('suggestions'):
                    success_msg += "\n\n💡 **Рекомендации:**\n"
                    for suggestion in result['suggestions']:
                        success_msg += f"{suggestion}\n"
                
                return json.dumps({
                    "status": "success",
                    "message": success_msg,
                    "link": result['link'],
                    "club_id": result['club_id'],
                    "club_name": result['club_name']
                }, ensure_ascii=False)
            else:
                # Handle validation errors
                error_msg = result.get('error', 'Unknown error')
                
                if result.get('validation_errors'):
                    error_msg = "❌ **Ошибки валидации:**\n\n"
                    for error in result['validation_errors']:
                        error_msg += f"{error}\n"
                    error_msg += "\n📝 Пожалуйста, исправьте ошибки и попробуйте снова."
                elif result.get('duplicate'):
                    error_msg += "\n\n💡 Попробуйте добавить город или специализацию к названию."
                
                return json.dumps({
                    "status": "error",
                    "message": error_msg,
                    "validation_errors": result.get('validation_errors', [])
                }, ensure_ascii=False)

        elif tool_name == 'get_my_clubs':
            clubs = self.service_provider.club_management_service.get_user_managed_clubs(user)
            if not clubs:
                return "You don't manage any clubs yet."
            return json.dumps(clubs, ensure_ascii=False)

        elif tool_name == 'update_club':
            club_id = args.get('club_id')
            # Filter out club_id from args to pass the rest as kwargs
            update_data = {k: v for k, v in args.items() if k != 'club_id'}
            
            result = self.service_provider.club_management_service.update_club_details(
                user, club_id, **update_data
            )
            return json.dumps(result, ensure_ascii=False)

        elif tool_name == 'create_event':
            club_id = args.get('club_id')
            title = args.get('title')
            description = args.get('description')
            start_datetime = args.get('start_datetime')
            end_datetime = args.get('end_datetime')
            location = args.get('location')
            # Optional args
            min_age = args.get('min_age')
            max_age = args.get('max_age')
            entry_requirements = args.get('entry_requirements')
            
            result = self.service_provider.club_management_service.create_event(
                user, club_id, title, description, start_datetime, end_datetime, location,
                min_age=min_age, max_age=max_age, entry_requirements=entry_requirements
            )
            return json.dumps(result, ensure_ascii=False)

        elif tool_name == 'create_post':
            club_id = args.get('club_id')
            title = args.get('title')
            content = args.get('content')
            
            result = self.service_provider.club_management_service.create_post(
                user, club_id, title, content
            )
            return json.dumps(result, ensure_ascii=False)

        return f"Error: Unknown tool {tool_name} for Club Agent"

    def _execute_support_tools(self, tool_name: str, args: Dict, user) -> str:
        if tool_name == 'get_platform_status':
            # Assuming PlatformServiceManager has get_status
            # If not, we might need to mock or implement it
            if hasattr(self.service_provider.platform_service_manager, 'get_status'):
                status = self.service_provider.platform_service_manager.get_status()
                return json.dumps(status, ensure_ascii=False)
            return "Platform status: All systems operational (Mocked)"
            
        elif tool_name == 'search_knowledge_base':
            query = args.get('query', '')
            kb_service = self.service_provider.knowledge_service
            results = kb_service.search(query)
            return kb_service.format_results(results)
            
        return f"Error: Unknown tool {tool_name} for Support Agent"


    def _execute_mentor_tools(self, tool_name: str, args: Dict, user) -> str:
        # Для анонимных пользователей возвращаем сообщение о необходимости авторизации
        if user is None:
            return "Для использования функций развития необходимо авторизоваться."
            
        dev_service = self.service_provider.development_service
        
        if tool_name == 'get_development_recommendations':
            message = args.get('message', '')
            result = dev_service.get_development_recommendations(user, message)
            return dev_service.format_development_recommendations(result)
            
        elif tool_name == 'get_my_progress':
            result = dev_service.get_user_development_progress(user)
            if not result['success']:
                return f"Error: {result.get('error')}"
            
            if result['total_active_plans'] == 0:
                return "You don't have any active development plans yet."
                
            response = "Your progress:\n"
            for plan in result['plans']:
                response += f"- {plan['path_title']}: {plan['overall_progress']}%\n"
            return response
            
        elif tool_name == 'start_development_path':
            path_id = args.get('path_id')
            result = dev_service.create_development_plan(user, path_id)
            if result['success']:
                return f"Successfully started plan: {result['path_title']}"
            return f"Failed to start plan: {result.get('error')}"
            
        return f"Error: Unknown tool {tool_name} for Mentor Agent"

