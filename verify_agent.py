#!/usr/bin/env python3
"""
Quick verification that the enhanced club creation agent is working
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Initialize Django
import django
django.setup()

async def verify_agent():
    """Verify the enhanced club creation agent is working"""
    print("🔍 Verifying Enhanced Club Creation Agent...")

    try:
        # Test imports
        from ai_consultant.agents.club_creation_agent import get_club_creation_agent
        from ai_consultant.api.club_creation_agent_api import ClubCreationAgentView
        print("✅ All imports successful")

        # Test agent creation
        agent = get_club_creation_agent()
        print("✅ Agent instance created")

        # Test session creation
        session = agent._get_or_create_session(1)
        print("✅ Session management working")

        # Test basic message processing
        test_message = "Хочу создать клуб по программированию для студентов"
        analysis = await agent._analyze_message(test_message, session)
        print(f"✅ Message analysis completed")
        print(f"   🎯 Intent: {analysis.get('intent', 'unknown')}")
        print(f"   📊 Complexity: {analysis.get('complexity', 'unknown')}")
        print(f"   🏷️ Category: {analysis.get('category', 'unknown')}")

        # Test API view creation
        api_view = ClubCreationAgentView()
        print("✅ API View created successfully")

        print("\n🎉 Enhanced Club Creation Agent is working perfectly!")
        print("✨ All components are functional and ready for use!")

        return True

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    try:
        success = asyncio.run(verify_agent())
        return 0 if success else 1
    except Exception as e:
        print(f"💥 Verification failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())