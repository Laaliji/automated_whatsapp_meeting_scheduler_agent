import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.core.config import get_settings
from app.models.database import SessionLocal, User

settings = get_settings()

class GoogleCalendarService:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/calendar']
        
    def get_user_credentials(self, phone_number: str) -> Optional[Credentials]:
        """Get stored credentials for user"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.phone_number == phone_number).first()
            if user and user.google_refresh_token:
                creds = Credentials(
                    token=None,
                    refresh_token=user.google_refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=settings.google_client_id,
                    client_secret=settings.google_client_secret,
                    scopes=self.scopes
                )
                
                # Refresh if needed
                if creds.expired:
                    creds.refresh(Request())
                    
                return creds
        finally:
            db.close()
        return None
    
    def create_event(self, phone_number: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Google Calendar event"""
        try:
            creds = self.get_user_credentials(phone_number)
            if not creds:
                return {"success": False, "error": "User not authenticated with Google"}
            
            service = build('calendar', 'v3', credentials=creds)
            
            # Create event object
            event = {
                'summary': event_data.get('title', 'Meeting'),
                'description': event_data.get('description', ''),
                'start': {
                    'dateTime': event_data['start_time'].isoformat(),
                    'timeZone': event_data.get('timezone', 'UTC'),
                },
                'end': {
                    'dateTime': event_data['end_time'].isoformat(),
                    'timeZone': event_data.get('timezone', 'UTC'),
                },
            }
            
            # Add location if provided
            if event_data.get('location'):
                event['location'] = event_data['location']
            
            # Add attendees if provided
            if event_data.get('attendees'):
                event['attendees'] = [{'email': email} for email in event_data['attendees']]
            
            # Create the event
            created_event = service.events().insert(calendarId='primary', body=event).execute()
            
            return {
                "success": True,
                "event_id": created_event['id'],
                "event_link": created_event.get('htmlLink')
            }
            
        except HttpError as e:
            return {"success": False, "error": f"Google Calendar API error: {e}"}
        except Exception as e:
            return {"success": False, "error": f"Calendar service error: {e}"}
    
    def update_event(self, phone_number: str, event_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing Google Calendar event"""
        try:
            creds = self.get_user_credentials(phone_number)
            if not creds:
                return {"success": False, "error": "User not authenticated with Google"}
            
            service = build('calendar', 'v3', credentials=creds)
            
            # Get existing event
            event = service.events().get(calendarId='primary', eventId=event_id).execute()
            
            # Update fields
            if 'title' in event_data:
                event['summary'] = event_data['title']
            if 'start_time' in event_data:
                event['start']['dateTime'] = event_data['start_time'].isoformat()
            if 'end_time' in event_data:
                event['end']['dateTime'] = event_data['end_time'].isoformat()
            if 'location' in event_data:
                event['location'] = event_data['location']
            
            # Update the event
            updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
            
            return {"success": True, "event_id": updated_event['id']}
            
        except HttpError as e:
            return {"success": False, "error": f"Google Calendar API error: {e}"}
        except Exception as e:
            return {"success": False, "error": f"Calendar service error: {e}"}
    
    def delete_event(self, phone_number: str, event_id: str) -> Dict[str, Any]:
        """Delete a Google Calendar event"""
        try:
            creds = self.get_user_credentials(phone_number)
            if not creds:
                return {"success": False, "error": "User not authenticated with Google"}
            
            service = build('calendar', 'v3', credentials=creds)
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            
            return {"success": True}
            
        except HttpError as e:
            return {"success": False, "error": f"Google Calendar API error: {e}"}
        except Exception as e:
            return {"success": False, "error": f"Calendar service error: {e}"}

# Global instance
calendar_service = GoogleCalendarService()