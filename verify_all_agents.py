import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_consultant.agents.registry import AgentRegistry
# Import agents to ensure they are registered
import ai_consultant.agents.specialists.club_agent
import ai_consultant.agents.specialists.mentor_agent
import ai_consultant.agents.specialists.support_agent
import ai_consultant.agents.specialists.orchestrator

def verify_all_agents():
    print("🤖 Starting Verification of All Agents...")
    
    agents = AgentRegistry.get_all_agents()
    print(f"Found {len(agents)} registered agents.")
    
    failed_agents = []
    
    for name, agent_cls in agents.items():
        print(f"\n--------------------------------------------------")
        print(f"Testing Agent: {name}")
        print(f"Class: {agent_cls.__name__}")
        
        try:
            # Instantiate
            agent = agent_cls()
            
            # Verify Name
            print(f"   Name: {agent.name}")
            if agent.name != name:
                print(f"   ⚠️ WARNING: Registered name '{name}' differs from agent.name '{agent.name}'")
            
            # Verify Description
            print(f"   Description: {agent.description}")
            
            # Verify System Prompt
            prompt = agent.get_system_prompt()
            if not isinstance(prompt, str) or len(prompt) == 0:
                print("   ❌ FAILURE: System prompt is empty or not a string.")
                failed_agents.append(name)
            else:
                print(f"   ✅ System Prompt: {len(prompt)} chars (Starts with: {prompt[:50]}...)")
                
            # Verify Tools
            tools = agent.get_tools()
            if not isinstance(tools, list):
                print("   ❌ FAILURE: get_tools did not return a list.")
                failed_agents.append(name)
            else:
                print(f"   ✅ Tools: {len(tools)} tools available.")
                for tool in tools:
                    print(f"      - {tool.get('function', {}).get('name', 'Unknown')}")

        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
            failed_agents.append(name)
            import traceback
            traceback.print_exc()

    print(f"\n--------------------------------------------------")
    if failed_agents:
        print(f"❌ Verification Failed for agents: {', '.join(failed_agents)}")
        sys.exit(1)
    else:
        print("✅ All Agents Verified Successfully!")

if __name__ == "__main__":
    verify_all_agents()
