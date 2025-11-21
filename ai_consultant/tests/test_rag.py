from unittest.mock import Mock
from django.test import TestCase
from ..services.knowledge import KnowledgeBaseService
from ..agents.tools import ToolExecutor

class TestRAG(TestCase):
    def setUp(self):
        self.kb_service = KnowledgeBaseService()
        self.service_provider = Mock()
        self.service_provider.knowledge_service = self.kb_service
        self.executor = ToolExecutor(self.service_provider)
        self.user = Mock()

    def test_search_knowledge_base(self):
        results = self.kb_service.search("password")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['title'], "How to reset password")
        
    def test_search_no_results(self):
        results = self.kb_service.search("xyz123notfound")
        self.assertEqual(len(results), 0)
        
    def test_format_results(self):
        results = [
            {"title": "Test Title", "content": "Test Content"}
        ]
        formatted = self.kb_service.format_results(results)
        self.assertIn("**Test Title**", formatted)
        self.assertIn("Test Content", formatted)

    def test_tool_execution_rag(self):
        result = self.executor.execute(
            'support_specialist',
            'search_knowledge_base',
            {'query': 'club creation'},
            self.user
        )
        
        self.assertIn("Creating a Club", result)
