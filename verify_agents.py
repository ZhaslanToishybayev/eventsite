import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from agents.services.club_manager import ClubManagerAgent
from agents.services.moderator import ModeratorAgent
from clubs.models import Club, ClubCategory
from accounts.models import User

def test_agents():
    print("Testing Agents...")
    
    # 1. Test Moderator
    print("\n--- Testing Moderator Agent ---")
    mod = ModeratorAgent()
    safe_text = "Hello, I love this club!"
    unsafe_text = "I hate everyone and I want to hurt them."
    
    print(f"Checking safe text: '{safe_text}'")
    res_safe = mod.check_content(safe_text)
    print(f"Result: {res_safe}")
    
    print(f"Checking unsafe text: '{unsafe_text}'")
    res_unsafe = mod.check_content(unsafe_text)
    print(f"Result: {res_unsafe}")

    # 2. Test Club Manager
    print("\n--- Testing Club Manager Agent ---")
    # Create dummy club if needed or get first
    try:
        club = Club.objects.first()
        if not club:
            print("No clubs found, creating dummy club...")
            user = User.objects.first()
            if not user:
                 print("No users found, cannot create club.")
                 return
            category, _ = ClubCategory.objects.get_or_create(name="Test Category")
            club = Club.objects.create(name="Test Club", description="A club for testing agents", creater=user, category=category)
        
        print(f"Using club: {club.name}")
        manager = ClubManagerAgent()
        events = manager.suggest_events(club)
        print(f"Suggested Events: {events}")
        
        announcement = manager.draft_announcement(club, "New Season Opening")
        print(f"Draft Announcement: {announcement}")
        
    except Exception as e:
        print(f"Club Manager Test Failed: {e}")

if __name__ == "__main__":
    test_agents()
