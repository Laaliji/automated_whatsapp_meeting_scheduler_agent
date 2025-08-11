import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.services.calendar_service import calendar_service
from app.services.todoist_service import todoist_service
from app.models.database import SessionLocal, User, Meeting
import logging

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.calendar_service = calendar_service
        self.todoist_service = todoist_service
    
    async def create_meeting(self, phone: str, meeting_data: dict) -> Dict[str, Any]:
        """Create a meeting in Google Calendar and schedule Todoist task"""
        
        db = SessionLocal()
        try:
            # Get or create user
            user = db.query(User).filter(User.phone_number == phone).first()
            if not user:
                user = User(phone_number=phone)
                db.add(user)
                db.commit()
                db.refresh(user)
            
            # Parse meeting details
            start_time = self._parse_datetime(meeting_data.get('date'), meeting_data.get('time'))
            duration = meeting_data.get('duration_minutes', 30)
            end_time = start_time + timedelta(minutes=duration)
            
            # Prepare event data for Google Calendar
            event_data = {
                'title': meeting_data.get('title', 'Meeting'),
                'start_time': start_time,
                'end_time': end_time,
                'location': meeting_data.get('location'),
                'timezone': meeting_data.get('timezone', 'UTC'),
                'attendees': meeting_data.get('participants', [])
            }
            
            # Create Google Calendar event
            calendar_result = self.calendar_service.create_event(phone, event_data)
            
            if not calendar_result['success']:
                return {'success': False, 'error': calendar_result['error']}
            
            # Create meeting record
            meeting = Meeting(
                user_id=user.id,
                google_event_id=calendar_result['event_id'],
                title=meeting_data.get('title', 'Meeting'),
                start_time=start_time,
                end_time=end_time,
                location=meeting_data.get('location'),
                meeting_type=meeting_data.get('meeting_type', 'in-person')
            )
            
            db.add(meeting)
            db.commit()
            db.refresh(meeting)
            
            # Create Todoist task for the meeting day
            await self._create_todoist_task(phone, meeting)
            
            return {
                'success': True,
                'meeting_id': meeting.id,
                'event_id': calendar_result['event_id']
            }
            
        except Exception as e:
            logger.error(f"Error creating meeting: {e}")
            db.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            db.close()
    
    def _parse_datetime(self, date_str: str, time_str: str) -> datetime:
        """Parse date and time strings into datetime object"""
        try:
            # Handle various date formats
            if date_str and time_str:
                date_part = datetime.strptime(date_str, '%Y-%m-%d').date()
                time_part = datetime.strptime(time_str, '%H:%M').time()
                return datetime.combine(date_part, time_part)
        except Exception as e:
            logger.error(f"Error parsing datetime: {e}")
            
        # Default to tomorrow at specified time or 10 AM
        tomorrow = datetime.now().date() + timedelta(days=1)
        try:
            time_part = datetime.strptime(time_str, '%H:%M').time() if time_str else datetime.strptime('10:00', '%H:%M').time()
        except:
            time_part = datetime.strptime('10:00', '%H:%M').time()
        
        return datetime.combine(tomorrow, time_part)
    
    async def _create_todoist_task(self, phone: str, meeting: Meeting):
        """Create Todoist task for the meeting"""
        try:
            task_content = f"📅 Meeting: {meeting.title}"
            if meeting.location:
                task_content += f" at {meeting.location}"
            
            task_description = f"Meeting scheduled for {meeting.start_time.strftime('%Y-%m-%d %H:%M')}"
            if meeting.meeting_type:
                task_description += f"\nType: {meeting.meeting_type}"
            
            # Create task data
            task_data = {
                'content': task_content,
                'description': task_description,
                'due_date': meeting.start_time.date(),
                'priority': 2,  # High priority
                'labels': ['meeting', 'scheduled']
            }
            
            # Create the task
            result = await self.todoist_service.create_task(phone, task_data)
            
            if result['success']:
                # Update meeting record with Todoist task ID
                db = SessionLocal()
                try:
                    meeting.todoist_task_id = result['task_id']
                    db.commit()
                    logger.info(f"Todoist task created for meeting {meeting.id}")
                finally:
                    db.close()
            else:
                logger.error(f"Failed to create Todoist task: {result['error']}")
                
        except Exception as e:
            logger.error(f"Error creating Todoist task: {e}")
    
    async def cancel_meeting(self, phone: str, meeting_id: int) -> Dict[str, Any]:
        """Cancel a meeting and associated tasks"""
        db = SessionLocal()
        try:
            meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
            if not meeting:
                return {'success': False, 'error': 'Meeting not found'}
            
            # Cancel Google Calendar event
            if meeting.google_event_id:
                calendar_result = self.calendar_service.delete_event(phone, meeting.google_event_id)
                if not calendar_result['success']:
                    logger.warning(f"Failed to delete calendar event: {calendar_result['error']}")
            
            # Cancel Todoist task
            if meeting.todoist_task_id:
                todoist_result = await self.todoist_service.delete_task(phone, meeting.todoist_task_id)
                if not todoist_result['success']:
                    logger.warning(f"Failed to delete Todoist task: {todoist_result['error']}")
            
            # Update meeting status
            meeting.status = 'cancelled'
            db.commit()
            
            return {'success': True, 'message': 'Meeting cancelled successfully'}
            
        except Exception as e:
            logger.error(f"Error cancelling meeting: {e}")
            db.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            db.close()