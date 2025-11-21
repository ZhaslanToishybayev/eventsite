from allauth.account.adapter import DefaultAccountAdapter
from django.forms import ValidationError

class CustomAccountAdapter(DefaultAccountAdapter):
    def clean_phone(self, phone):
        # Custom phone validation logic here if needed
        return phone

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        # Ensure phone is set if not provided by social provider
        if not user.phone:
            # Generate a temporary phone or handle it as needed
            # For Google Auth, phone is usually not provided
            # You might want to redirect to a profile completion page
            pass
        return user

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        # Map social data to user fields
        user.first_name = data.get('first_name') or data.get('given_name') or 'User'
        user.last_name = data.get('last_name') or data.get('family_name') or 'Google'
        
        # Handle phone number if available (unlikely for Google)
        # user.phone = ... 
        
        # If phone is required by your model, you might need to set a dummy one
        # or handle it in a signal/form
        if not user.phone:
             # Generate a dummy phone to satisfy unique constraint temporarily
             # Ideally, redirect user to fill in phone
             import uuid
             user.phone = f"+7000{str(uuid.uuid4().int)[:7]}" 
             
        return user
