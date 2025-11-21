#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from openai import OpenAI
from django.conf import settings

print("Testing OpenAI API...")
print(f"Model: {settings.OPENAI_MODEL}")
print(f"API Key (first 20 chars): {settings.OPENAI_API_KEY[:20]}...")

try:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Simple test
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "user", "content": "Say 'test'"}
        ],
        max_tokens=10
    )
    
    print("\n✅ SUCCESS!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"Error type: {type(e).__name__}")
