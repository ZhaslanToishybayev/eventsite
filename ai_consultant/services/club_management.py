from typing import Dict, Any, List, Optional
import logging
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from accounts.models import User
from clubs.models import Club, ClubEvent, ClubPost

logger = logging.getLogger(__name__)

class ClubManagementService:
    """
    Service for managing club-related operations: updating details, creating events, and posts.
    Designed to be used by AI Agents and API views.
    """

    def get_user_managed_clubs(self, user: User) -> List[Dict[str, Any]]:
        """
        Returns a list of clubs managed by the user.
        """
        if not user.is_authenticated:
            return []
            
        # User can manage clubs they created OR where they are a manager
        clubs = Club.objects.filter(creater=user) | user.managed_clubs.all()
        clubs = clubs.distinct()
        
        return [
            {
                'id': str(club.id),
                'name': club.name,
                'role': 'Creator' if club.creater == user else 'Manager'
            }
            for club in clubs
        ]

    def _get_club_if_allowed(self, user: User, club_id: str) -> Club:
        """
        Helper to get a club and verify user permissions.
        """
        club = get_object_or_404(Club, id=club_id)
        
        # Check permissions
        if club.creater != user and user not in club.managers.all():
            raise PermissionDenied(f"User {user.email} is not a manager of club {club.name}")
            
        return club

    def update_club_details(self, user: User, club_id: str, **kwargs) -> Dict[str, Any]:
        """
        Updates club details.
        Allowed kwargs: name, description, address, email, phone, whatsapp_group_link
        """
        try:
            club = self._get_club_if_allowed(user, club_id)
            
            allowed_fields = ['name', 'description', 'address', 'email', 'phone', 'whatsapp_group_link']
            updated_fields = []
            
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    setattr(club, field, value)
                    updated_fields.append(field)
            
            if updated_fields:
                club.save()
                return {
                    "success": True,
                    "message": f"Club updated successfully. Fields changed: {', '.join(updated_fields)}",
                    "club_name": club.name
                }
            else:
                return {
                    "success": False,
                    "message": "No valid fields provided for update."
                }
                
        except PermissionDenied as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Error updating club: {e}")
            return {"success": False, "error": str(e)}

    def create_event(self, user: User, club_id: str, title: str, description: str, 
                    start_datetime, end_datetime, location: str, **kwargs) -> Dict[str, Any]:
        """
        Creates a new event for the club.
        """
        try:
            club = self._get_club_if_allowed(user, club_id)
            
            event = ClubEvent.objects.create(
                club=club,
                title=title,
                description=description,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                location=location,
                min_age=kwargs.get('min_age'),
                max_age=kwargs.get('max_age'),
                entry_requirements=kwargs.get('entry_requirements')
            )
            
            return {
                "success": True,
                "message": f"Event '{title}' created successfully!",
                "event_id": str(event.id),
                "link": event.get_absolute_url()
            }
            
        except PermissionDenied as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return {"success": False, "error": str(e)}

    def create_post(self, user: User, club_id: str, title: str, content: str) -> Dict[str, Any]:
        """
        Creates a new news post for the club.
        """
        try:
            club = self._get_club_if_allowed(user, club_id)
            
            post = ClubPost.objects.create(
                club=club,
                title=title,
                content=content,
                is_published=True
            )
            
            return {
                "success": True,
                "message": f"Post '{title}' published successfully!",
                "post_id": str(post.id),
                "link": f"/clubs/post/{post.id}/" # Assuming URL structure, might need adjustment
            }
            
        except PermissionDenied as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Error creating post: {e}")
            return {"success": False, "error": str(e)}
