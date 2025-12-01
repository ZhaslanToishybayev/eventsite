#!/usr/bin/env python3
"""
Quick test of the enhanced club creation agent functionality
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

async def test_agent_basic():
    """Test basic agent functionality"""
    print("🔍 Testing basic agent functionality...")

    try:
        from ai_consultant.agents.club_creation_agent import get_club_creation_agent

        # Get agent instance
        agent = get_club_creation_agent()
        print("✅ Agent instance created successfully")

        # Test session creation
        session = agent._get_or_create_session(1)
        print("✅ Session created successfully")

        # Test basic message analysis
        test_message = "Хочу создать клуб по программированию"
        analysis = await agent._analyze_message(test_message, session)
        print(f"✅ Message analysis completed")
        print(f"   🎯 Intent: {analysis.get('intent', 'unknown')}")
        print(f"   📊 Complexity: {analysis.get('complexity', 'unknown')}")
        print(f"   🏷️ Category: {analysis.get('category', 'unknown')}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    try:
        success = asyncio.run(test_agent_basic())
        if success:
            print("\n🎉 Basic agent functionality working!")
            print("✨ The enhanced club creation agent is ready for use!")
        else:
            print("\n💥 Agent functionality test failed.")
        return 0 if success else 1
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())