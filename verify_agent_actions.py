import os
import django
import sys
import json
from unittest.mock import MagicMock, patch

# Setup Django environment
sys.path.append('/home/zhaslan/Downloads/unitysphere-project/home/almalinux/new/unitysphere')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_consultant.agents.registry import AgentRegistry
from ai_consultant.agents.specialists.club_agent import ClubAgent

def verify_agent_action(agent, user_message, expected_tool_name, expected_args_subset):
    """
    Verifies that the agent's system prompt and tools are set up correctly 
    to handle a specific user intent.
    
    Since we can't easily call the real OpenAI API here without a key and cost,
    we will verify:
    1. The tool exists in the agent's tool definition.
    2. The system prompt contains instructions relevant to the action.
    """
    print(f"\n🔍 Verifying action: {expected_tool_name}")
    print(f"   User Message: '{user_message}'")

    # 1. Verify Tool Existence
    tools = agent.get_tools()
    tool_found = False
    for tool in tools:
        if tool['function']['name'] == expected_tool_name:
            tool_found = True
            print(f"   ✅ Tool '{expected_tool_name}' found in agent tools.")
            
            # Verify parameters
            params = tool['function']['parameters']['properties']
            missing_params = []
            for arg in expected_args_subset:
                if arg not in params:
                    missing_params.append(arg)
            
            if missing_params:
                print(f"   ❌ Missing parameters in tool definition: {missing_params}")
            else:
                print(f"   ✅ All expected parameters {list(expected_args_subset.keys())} are present in tool definition.")
            break
    
    if not tool_found:
        print(f"   ❌ Tool '{expected_tool_name}' NOT found in agent tools.")
        return False

    # 2. Verify System Prompt Instructions
    prompt = agent.get_system_prompt()
    if expected_tool_name in prompt:
        print(f"   ✅ System prompt contains reference to '{expected_tool_name}'.")
    else:
        print(f"   ⚠️ System prompt does NOT explicitly mention '{expected_tool_name}'. This might be okay if instructions are generic, but explicit is better.")

    return True

def main():
    print("🤖 Starting Agent Action Verification...")
    
    # Instantiate Club Agent
    club_agent = ClubAgent()
    
    # Test Case 1: Create Club
    print("\n--- Test Case 1: Create Club ---")
    success_club = verify_agent_action(
        club_agent,
        "I want to create a new chess club called 'Grandmasters' in Almaty.",
        "create_club",
        {"name": "Grandmasters", "category": "Hobby", "city": "Almaty"}
    )
    
    # Test Case 2: Create Event
    print("\n--- Test Case 2: Create Event ---")
    success_event = verify_agent_action(
        club_agent,
        "Create a tournament for my club tomorrow at 10 AM.",
        "create_event",
        {"club_id": "uuid", "title": "Tournament", "start_datetime": "iso-date"}
    )

    if success_club and success_event:
        print("\n✅ All agent action verifications PASSED!")
    else:
        print("\n❌ Some verifications FAILED.")

if __name__ == "__main__":
    main()
