#!/usr/bin/env python3
"""
Simple test to verify the enhanced club creation agent imports work
"""

import os
import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Initialize Django
import django
django.setup()

def test_simple_import():
    """Test basic imports"""
    print("🔍 Testing basic imports...")

    try:
        # Test Django models import
        from clubs.models import UserInterest, UserInteraction
        print("✅ UserInterest and UserInteraction models imported successfully")

        # Test agent import
        from ai_consultant.agents.club_creation_agent import get_club_creation_agent
        print("✅ Club Creation Agent imported successfully")

        # Test API import
        from ai_consultant.api.club_creation_agent_api import ClubCreationAgentView
        print("✅ Club Creation Agent API imported successfully")

        return True

    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_import()
    if success:
        print("\n🎉 All imports working correctly!")
    else:
        print("\n💥 Some imports failed.")
    sys.exit(0 if success else 1)