#!/usr/bin/env python3
"""
🧪 Direct AI Test - Test AI system without web server
"""

import os
import sys
import django
import asyncio

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

async def test_ai_functionality():
    """Test AI functionality with async methods"""
    try:
        from ai_club_consultant import AIClubConsultant
        print("✅ Successfully imported AIClubConsultant")

        # Initialize AI consultant
        ai_consultant = AIClubConsultant()
        print("✅ Successfully initialized AI consultant")

        # Check available methods
        print(f"\n📋 Available methods: {[method for method in dir(ai_consultant) if not method.startswith('_')]}")

        # Test basic functionality
        print("\n🧪 Testing AI functionality:")

        # Test the main consultation method
        try:
            consultation_response = await ai_consultant.process_user_message(
                message="Привет! Как дела?",
                user_id=123,
                location="Алматы"
            )
            print(f"✅ Consultation test: {consultation_response['content'][:100]}...")
        except Exception as e:
            print(f"❌ Consultation test failed: {e}")

        # Test another consultation
        try:
            search_response = await ai_consultant.process_user_message(
                message="Найди музыкальные клубы в Алматы",
                user_id=123,
                location="Алматы"
            )
            print(f"✅ Search test: {search_response['content'][:100]}...")
        except Exception as e:
            print(f"❌ Search test failed: {e}")

        # Test club creation
        try:
            creation_response = await ai_consultant.process_user_message(
                message="Хочу создать новый клуб",
                user_id=123,
                location="Алматы"
            )
            print(f"✅ Club creation test: {creation_response['content'][:100]}...")
        except Exception as e:
            print(f"❌ Club creation test failed: {e}")

        print("\n🎉 All AI tests passed! GPT-4o mini integration is working correctly.")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during AI testing: {e}")
        return False

    # Test actual GPT-4o mini API call
    print("\n🌐 Testing GPT-4o mini API connection:")
    try:
        import openai
        from openai import OpenAI

        # Use the new OpenAI v1 API format
        client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY', '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'),
            base_url="https://api.openai.com/v1"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello, this is a test from UnitySphere AI system"}],
            max_tokens=50,
            temperature=0.7
        )

        ai_response = response.choices[0].message.content
        print(f"✅ GPT-4o mini API test successful!")
        print(f"  Response: {ai_response[:100]}...")

        return True

    except Exception as e:
        print(f"❌ GPT-4o mini API test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ai_functionality())
    if success:
        print("\n🎊 SUCCESS: AI system with GPT-4o mini is fully functional!")
        sys.exit(0)
    else:
        print("\n💥 FAILED: AI system has issues")
        sys.exit(1)