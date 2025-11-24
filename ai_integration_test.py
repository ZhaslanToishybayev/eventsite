#!/usr/bin/env python3
"""
Django Management Command for AI Agent Integration
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
import sys

# Add the project directory to Python path
sys.path.append('/var/www/myapp/eventsite')

class Command(BaseCommand):
    help = 'Test AI Agent integration with UnitySphere'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Run AI agent tests',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🤖 Starting UnitySphere AI Agent Integration...')
        )

        try:
            # Import AI agent
            from ai_agent import UnitySphereAIAgent

            # Initialize AI agent
            agent = UnitySphereAIAgent()

            self.stdout.write('✅ AI Agent initialized successfully')

            if options['test']:
                self.test_ai_agent(agent)

        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to import AI agent: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during AI integration: {e}')
            )

    def test_ai_agent(self, agent):
        """Test AI agent functionality"""
        self.stdout.write('\n🧪 Running AI Agent Tests...')

        try:
            # Test 1: Club creation advice
            self.stdout.write('\n1. Testing club creation advice...')
            advice = agent.get_club_creation_advice(
                "киберспорт",
                "CS:GO, Dota 2, Valorant",
                "объединить игроков, организовывать турниры"
            )
            self.stdout.write(f'✅ Club advice generated: {len(advice)} characters')

            # Test 2: Event ideas
            self.stdout.write('\n2. Testing event ideas generation...')
            ideas = agent.get_event_ideas(
                "киберспортивный клуб",
                "средний",
                "20-50 человек"
            )
            self.stdout.write(f'✅ Event ideas generated: {len(ideas)} characters')

            # Test 3: Community tips
            self.stdout.write('\n3. Testing community engagement tips...')
            tips = agent.get_community_engagement_tips(
                "киберспортивный клуб",
                "30"
            )
            self.stdout.write(f'✅ Community tips generated: {len(tips)} characters')

            # Test 4: General question
            self.stdout.write('\n4. Testing general question answering...')
            answer = agent.answer_general_question(
                "Как создать фан-клуб на fan-club.kz?"
            )
            self.stdout.write(f'✅ General answer generated: {len(answer)} characters')

            self.stdout.write(
                self.style.SUCCESS('\n🎉 All AI agent tests passed successfully!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ AI agent test failed: {e}')
            )

# Standalone execution for testing
if __name__ == "__main__":
    import django
    from django.conf import settings
    from django.test.utils import get_runner

    # Configure Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

    try:
        django.setup()

        # Create command instance and run
        command = Command()
        command.handle(test=True)

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Django is properly configured and .env file exists")