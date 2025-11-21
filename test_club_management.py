import os
import django
import sys
from django.utils import timezone
from datetime import timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User
from clubs.models import Club, ClubCategory, City
from ai_consultant.services.club_management import ClubManagementService

def test_club_management():
    print("🚀 Starting ClubManagementService verification...")
    
    # 1. Setup Data
    email = "test_manager@example.com"
    user, created = User.objects.get_or_create(email=email)
    if created:
        user.set_password("password123")
        user.save()
        print(f"✅ Created test user: {email}")
    else:
        print(f"ℹ️ Using existing test user: {email}")

    category, _ = ClubCategory.objects.get_or_create(name="Test Category")
    
    # Create a club managed by this user
    club_name = "AI Test Club"
    club, created = Club.objects.get_or_create(
        name=club_name,
        defaults={
            'creater': user,
            'category': category,
            'description': "A club for testing AI features"
        }
    )
    if created:
        print(f"✅ Created test club: {club_name}")
    else:
        print(f"ℹ️ Using existing test club: {club_name}")
        
    # Ensure user is creator (for permission check)
    if club.creater != user:
        club.creater = user
        club.save()

    service = ClubManagementService()

    # 2. Test get_user_managed_clubs
    print("\n🔍 Testing get_user_managed_clubs...")
    my_clubs = service.get_user_managed_clubs(user)
    found = any(c['id'] == str(club.id) for c in my_clubs)
    if found:
        print("✅ get_user_managed_clubs returned the test club.")
    else:
        print("❌ get_user_managed_clubs FAILED to return the test club.")
        return

    # 3. Test create_post
    print("\n📰 Testing create_post...")
    post_title = "AI News Post"
    post_content = "<p>This is a test post created by the script.</p>"
    
    result = service.create_post(user, str(club.id), post_title, post_content)
    
    if result['success']:
        print(f"✅ Post created successfully! ID: {result.get('post_id')}")
        # Verify in DB
        if club.posts.filter(title=post_title).exists():
            print("✅ Post found in database.")
        else:
            print("❌ Post NOT found in database.")
    else:
        print(f"❌ Failed to create post: {result.get('error')}")

    # 4. Test create_event
    print("\n📅 Testing create_event...")
    event_title = "AI Test Event"
    start = timezone.now() + timedelta(days=1)
    end = start + timedelta(hours=2)
    
    result = service.create_event(
        user, str(club.id), 
        title=event_title,
        description="Testing event creation",
        start_datetime=start,
        end_datetime=end,
        location="Test Location"
    )
    
    if result['success']:
        print(f"✅ Event created successfully! ID: {result.get('event_id')}")
    else:
        print(f"❌ Failed to create event: {result.get('error')}")

    # 5. Test update_club
    print("\n✏️ Testing update_club...")
    new_desc = "Updated description by script"
    result = service.update_club_details(user, str(club.id), description=new_desc)
    
    if result['success']:
        club.refresh_from_db()
        if club.description == new_desc:
            print("✅ Club description updated successfully.")
        else:
            print("❌ Club description mismatch in DB.")
    else:
        print(f"❌ Failed to update club: {result.get('error')}")

    print("\n🎉 Verification Complete!")

if __name__ == "__main__":
    test_club_management()
