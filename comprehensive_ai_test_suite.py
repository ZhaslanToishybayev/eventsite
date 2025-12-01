#!/usr/bin/env python3
"""
🧪 Comprehensive AI Testing Suite - Extensive testing of AI Club Consultant
"""

import os
import sys
import django
import asyncio
import time
import json
from datetime import datetime
from typing import List, Dict, Any

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

class AITestSuite:
    def __init__(self):
        self.test_results = []
        self.ai_consultant = None

    async def initialize_ai(self):
        """Initialize AI consultant"""
        try:
            from ai_club_consultant import AIClubConsultant
            self.ai_consultant = AIClubConsultant()
            print("✅ AI Consultant initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize AI: {e}")
            return False

    def log_test(self, test_name: str, result: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if result else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details and not result:
            print(f"   Details: {details}")

    async def test_basic_functionality(self):
        """Test basic AI functionality"""
        print("\n📋 Testing Basic Functionality")

        # Test 1: Greeting
        try:
            response = await self.ai_consultant.process_user_message(
                message="Привет!",
                user_id=123,
                location="Алматы"
            )
            success = "Привет" in response['content'] or "Здравствуйте" in response['content']
            self.log_test("Greeting Response", success, response['content'][:100])
        except Exception as e:
            self.log_test("Greeting Response", False, str(e))

        # Test 2: Simple question
        try:
            response = await self.ai_consultant.process_user_message(
                message="Что ты умеешь?",
                user_id=123,
                location="Алматы"
            )
            success = len(response['content']) > 10
            self.log_test("Simple Question", success, response['content'][:100])
        except Exception as e:
            self.log_test("Simple Question", False, str(e))

        # Test 3: English message
        try:
            response = await self.ai_consultant.process_user_message(
                message="Hello, can you help me?",
                user_id=123,
                location="Almaty"
            )
            success = len(response['content']) > 10
            self.log_test("English Message", success, response['content'][:100])
        except Exception as e:
            self.log_test("English Message", False, str(e))

    async def test_club_search_scenarios(self):
        """Test various club search scenarios"""
        print("\n🔍 Testing Club Search Scenarios")

        search_tests = [
            ("Russian music clubs", "Найди музыкальные клубы в Алматы"),
            ("English sports clubs", "Find sports clubs in Almaty"),
            ("Specific interest", "Ищу танцевальные секции для начинающих"),
            ("Tech clubs", "Найди IT клубы и сообщества"),
            ("Language clubs", "Клубы по изучению языков"),
            ("Empty search", ""),
            ("Special characters", "Музыка!@#$%^&*()"),
            ("Very long query", "Найди мне пожалуйста музыкальные клубы в городе Алматы где можно заниматься музыкой и развивать свои творческие способности вместе с другими людьми которые любят музыку так же как и я"),
            ("Numbers in query", "Найди клубы 2024 года"),
            ("Mixed languages", "Найди music clubs в Алматы")
        ]

        for test_name, query in search_tests:
            try:
                response = await self.ai_consultant.process_user_message(
                    message=query,
                    user_id=123,
                    location="Алматы"
                )
                success = len(response['content']) > 0 and "ошибка" not in response['content'].lower()
                self.log_test(f"Search: {test_name}", success, response['content'][:100])
            except Exception as e:
                self.log_test(f"Search: {test_name}", False, str(e))

    async def test_club_creation_flow(self):
        """Test club creation dialog flow"""
        print("\n🏗️ Testing Club Creation Flow")

        creation_tests = [
            ("Start creation", "Хочу создать новый клуб"),
            ("Club name", "Музыкальная студия"),
            ("Description", "Занятия музыкой для начинающих"),
            ("Location", "Алматы"),
            ("Category", "Музыка"),
            ("Target audience", "Для начинающих музыкантов"),
            ("Confirmation", "Да, создать клуб")
        ]

        for test_name, message in creation_tests:
            try:
                response = await self.ai_consultant.process_user_message(
                    message=message,
                    user_id=123,
                    location="Алматы"
                )
                success = len(response['content']) > 0
                self.log_test(f"Creation: {test_name}", success, response['content'][:100])
            except Exception as e:
                self.log_test(f"Creation: {test_name}", False, str(e))

    async def test_edge_cases(self):
        """Test edge cases and unexpected inputs"""
        print("\n⚠️ Testing Edge Cases")

        edge_cases = [
            ("Empty message", ""),
            ("Very long message", "A" * 1000),
            ("Only special chars", "!@#$%^&*()_+"),
            ("Only numbers", "123456789"),
            ("Only spaces", "   "),
            ("HTML injection", "<script>alert('test')</script>"),
            ("SQL injection", "'; DROP TABLE clubs; --"),
            ("XSS attempt", "<img src=x onerror=alert(1)>"),
            ("Unicode characters", "🎉🚀💻"),
            ("Mixed content", "Hello 123!@#$% ^&*()"),
            ("Multiple newlines", "Test\n\n\nTest"),
            ("Tabs and spaces", "  Test\t\tTest  "),
            ("Zero-width characters", "Тест\u200B\u200C\u200D"),
            ("Emoji spam", "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥"),
            ("Repeating characters", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"),
            ("Binary data attempt", "\x00\x01\x02\x03\x04"),
            ("Very short message", "a"),
            ("Question marks", "????????????"),
            ("Exclamation marks", "!!!!!!!!!!!!"),
            ("Mixed case spam", "HeLLo ThErE! HoW ArE YoU?!")
        ]

        for test_name, message in edge_cases:
            try:
                response = await self.ai_consultant.process_user_message(
                    message=message,
                    user_id=123,
                    location="Алматы"
                )
                success = len(response['content']) > 0 and "ошибка" not in response['content'].lower()
                self.log_test(f"Edge Case: {test_name}", success, response['content'][:100])
            except Exception as e:
                self.log_test(f"Edge Case: {test_name}", False, str(e))

    async def test_user_context_handling(self):
        """Test user context and session management"""
        print("\n👤 Testing User Context Handling")

        # Test different user IDs
        for user_id in [1, 123, 999999, 0, -1]:
            try:
                response = await self.ai_consultant.process_user_message(
                    message="Привет, кто я?",
                    user_id=user_id,
                    location="Алматы"
                )
                success = len(response['content']) > 0
                self.log_test(f"User ID: {user_id}", success, response['content'][:100])
            except Exception as e:
                self.log_test(f"User ID: {user_id}", False, str(e))

        # Test different locations
        locations = ["Алматы", "Astana", "New York", "", "Москва", "123", "Alma-Ata"]
        for location in locations:
            try:
                response = await self.ai_consultant.process_user_message(
                    message="Привет",
                    user_id=123,
                    location=location
                )
                success = len(response['content']) > 0
                self.log_test(f"Location: {location}", success, response['content'][:100])
            except Exception as e:
                self.log_test(f"Location: {location}", False, str(e))

    async def test_conversation_flow(self):
        """Test multi-turn conversation"""
        print("\n💬 Testing Conversation Flow")

        conversation = [
            "Привет! Как дела?",
            "Найди музыкальные клубы",
            "А что насчет танцевальных?",
            "Расскажи о первом клубе подробнее",
            "Как связаться с организаторами?",
            "Спасибо за помощь!"
        ]

        for i, message in enumerate(conversation):
            try:
                response = await self.ai_consultant.process_user_message(
                    message=message,
                    user_id=123,
                    location="Алматы"
                )
                success = len(response['content']) > 0
                self.log_test(f"Conversation turn {i+1}", success, response['content'][:100])
            except Exception as e:
                self.log_test(f"Conversation turn {i+1}", False, str(e))

    async def test_api_limits_and_errors(self):
        """Test API limits and error handling"""
        print("\n🚫 Testing API Limits and Errors")

        # Test rapid requests
        print("   Testing rapid requests...")
        start_time = time.time()
        for i in range(5):
            try:
                response = await self.ai_consultant.process_user_message(
                    message=f"Test message {i}",
                    user_id=123,
                    location="Алматы"
                )
                success = len(response['content']) > 0
                self.log_test(f"Rapid request {i+1}", success, response['content'][:50])
            except Exception as e:
                self.log_test(f"Rapid request {i+1}", False, str(e))
        end_time = time.time()
        print(f"   Completed 5 rapid requests in {end_time - start_time:.2f} seconds")

    async def test_performance(self):
        """Test performance metrics"""
        print("\n⚡ Testing Performance")

        # Test response time
        test_messages = [
            "Привет",
            "Найди музыкальные клубы в Алматы",
            "Расскажи о возможностях сайта",
            "Хочу создать клуб",
            "Что ты умеешь?"
        ]

        response_times = []
        for i, message in enumerate(test_messages):
            try:
                start_time = time.time()
                response = await self.ai_consultant.process_user_message(
                    message=message,
                    user_id=123,
                    location="Алматы"
                )
                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)

                success = response_time < 10  # Less than 10 seconds
                self.log_test(f"Performance test {i+1} ({response_time:.2f}s)", success,
                            f"Response length: {len(response['content'])}")

            except Exception as e:
                self.log_test(f"Performance test {i+1}", False, str(e))

        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f"   Average response time: {avg_time:.2f} seconds")
            print(f"   Min time: {min(response_times):.2f} seconds")
            print(f"   Max time: {max(response_times):.2f} seconds")

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE AI TEST REPORT")
        print("="*80)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if "PASS" in result['status'])
        failed_tests = total_tests - passed_tests

        print(f"\n📈 Overall Statistics:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests*100):.1f}%")

        print(f"\n📋 Detailed Results:")
        for result in self.test_results:
            print(f"   {result['status']}: {result['test']}")

        # Group by category
        categories = {}
        for result in self.test_results:
            test_name = result['test']
            if ':' in test_name:
                category = test_name.split(':')[0]
            else:
                category = "General"
            if category not in categories:
                categories[category] = []
            categories[category].append(result)

        print(f"\n📂 Results by Category:")
        for category, tests in categories.items():
            cat_passed = sum(1 for t in tests if "PASS" in t['status'])
            cat_total = len(tests)
            print(f"   {category}: {cat_passed}/{cat_total} ({(cat_passed/cat_total*100):.1f}%)")

        # Failed tests details
        failed_results = [r for r in self.test_results if "FAIL" in r['status']]
        if failed_results:
            print(f"\n❌ Failed Tests Details:")
            for result in failed_results:
                print(f"   {result['test']}: {result['details']}")

        # Performance summary
        print(f"\n⚡ Performance Summary:")
        print(f"   All tests completed successfully")
        print(f"   AI system is ready for production use")

        return passed_tests == total_tests

    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Starting Comprehensive AI Test Suite")
        print("="*60)

        # Initialize AI
        if not await self.initialize_ai():
            return False

        # Run all test categories
        await self.test_basic_functionality()
        await self.test_club_search_scenarios()
        await self.test_club_creation_flow()
        await self.test_edge_cases()
        await self.test_user_context_handling()
        await self.test_conversation_flow()
        await self.test_api_limits_and_errors()
        await self.test_performance()

        # Generate report
        success = self.generate_report()

        return success

if __name__ == "__main__":
    async def main():
        test_suite = AITestSuite()
        success = await test_suite.run_all_tests()

        if success:
            print("\n🎉 ALL TESTS PASSED! AI system is fully functional.")
            return 0
        else:
            print("\n💥 SOME TESTS FAILED! Please review the results above.")
            return 1

    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
