import os
import django
import sys
import time

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from clubs.models import Club, ClubCategory
from ai_consultant.services.rag_service import get_rag_service

def test_rag_functionality():
    print("🔍 Starting RAG Context Verification...")
    
    rag_service = get_rag_service()
    
    # 1. Create a unique dummy club
    unique_id = int(time.time())
    club_name = f"TestClub_{unique_id}"
    club_desc = f"This is a unique test club for RAG verification. Secret code: {unique_id}"
    
    print(f"\n1. Creating dummy club: {club_name}")
    
    try:
        # Get or create a user for the creator
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            email='rag_test_user@example.com', 
            defaults={
                'first_name': 'RAG', 
                'last_name': 'Tester',
                'phone': f'+7700{unique_id}'[:12]  # Ensure unique phone
            }
        )

        category, _ = ClubCategory.objects.get_or_create(name="Test Category", defaults={"is_active": True})
        club = Club.objects.create(
            name=club_name,
            description=club_desc,
            category=category,
            creater=user,
            is_active=True
        )
        print("   ✅ Club created in DB")
        
        # 2. Index the club
        print("\n2. Indexing club data...")
        # We can call index_club_data, but it might be slow if there are many clubs.
        # For this test, let's manually add this specific club to ensure it's in the index immediately.
        # But to test the REAL flow, we should use the method. Let's try the method first.
        rag_service.index_club_data()
        print("   ✅ Indexing triggered")
        
        # 3. Query for the club
        print(f"\n3. Querying RAG for '{club_name}'...")
        query = f"Tell me about {club_name}"
        context = rag_service.get_enhanced_context(query)
        
        # 4. Verify results
        print("\n4. Verifying Context...")
        found = False
        if 'retrieved_info' in context and 'clubs' in context['retrieved_info']:
            for doc in context['retrieved_info']['clubs']:
                print(f"   Found doc: {doc['text'][:100]}...")
                if str(unique_id) in doc['text']:
                    found = True
                    break
        
        if found:
            print(f"   ✅ SUCCESS: Found secret code {unique_id} in RAG context!")
        else:
            print(f"   ❌ FAILURE: Did not find secret code {unique_id} in RAG context.")
            print("   Full Context:", context)

        # 5. Test Hallucination (Negative Test)
        print("\n5. Testing Hallucination (Negative Test)...")
        fake_club = f"NonExistentClub_{unique_id}"
        query_fake = f"Tell me about {fake_club}"
        context_fake = rag_service.get_enhanced_context(query_fake)
        
        fake_found = False
        if 'retrieved_info' in context_fake and 'clubs' in context_fake['retrieved_info']:
            for doc in context_fake['retrieved_info']['clubs']:
                if fake_club in doc['text']:
                    fake_found = True
                    break
        
        if not fake_found:
            print("   ✅ SUCCESS: Did not find non-existent club in context.")
        else:
            print("   ❌ FAILURE: Found non-existent club in context (Hallucination risk).")

    except Exception as e:
        print(f"\n❌ Error during RAG verification: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\nCleaning up...")
        if 'club' in locals():
            club.delete()
            print("   Test club deleted from DB")

if __name__ == "__main__":
    test_rag_functionality()
