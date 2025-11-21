import json
from unittest.mock import Mock, MagicMock
from django.test import TestCase
from ..agents.tools import ToolExecutor

class TestToolExecutor(TestCase):
    def setUp(self):
        self.service_provider = Mock()
        self.user = Mock()
        self.executor = ToolExecutor(self.service_provider)

    def test_execute_club_search(self):
        # Mock service provider method
        self.service_provider.get_clubs_by_interest_keywords.return_value = {
            'success': True,
            'message': 'Found clubs',
            'clubs': []
        }
        self.service_provider.format_club_recommendations.return_value = "Formatted Club List"
        
        result = self.executor.execute(
            'club_specialist', 
            'search_clubs', 
            {'query': 'chess'}, 
            self.user
        )
        
        self.service_provider.get_clubs_by_interest_keywords.assert_called_with('chess', 5)
        self.assertEqual(result, "Formatted Club List")

    def test_execute_support_status(self):
        # Mock platform service
        self.service_provider.platform_service_manager.get_status.return_value = {'status': 'ok'}
        
        result = self.executor.execute(
            'support_specialist',
            'get_platform_status',
            {},
            self.user
        )
        
        self.assertEqual(result, '{"status": "ok"}')

    def test_execute_mentor_recommendations(self):
        # Mock development service
        dev_service = Mock()
        self.service_provider.development_service = dev_service
        dev_service.get_development_recommendations.return_value = {}
        dev_service.format_development_recommendations.return_value = "Formatted Recommendations"
        
        result = self.executor.execute(
            'mentor_specialist',
            'get_development_recommendations',
            {'message': 'learn python'},
            self.user
        )
        
        dev_service.get_development_recommendations.assert_called_with(self.user, 'learn python')
        self.assertEqual(result, "Formatted Recommendations")

    def test_unknown_agent(self):
        result = self.executor.execute('unknown', 'tool', {}, self.user)
        self.assertTrue("Error: Unknown agent" in result)

    def test_unknown_tool(self):
        result = self.executor.execute('club_specialist', 'unknown_tool', {}, self.user)
        self.assertTrue("Error: Unknown tool" in result)
