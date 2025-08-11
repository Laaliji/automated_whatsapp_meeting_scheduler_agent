import httpx
from typing import Dict, Any, Optional
from datetime import datetime, date
from app.core.config import get_settings
from app.models.database import SessionLocal, User

settings = get_settings()

class TodoistService:
    def __init__(self):
        self.base_url = "https://api.todoist.com/rest/v2"
        
    def get_user_token(self, phone_number: str) -> Optional[str]:
        """Get stored Todoist token for user"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.phone_number == phone_number).first()
            return user.todoist_token if user else None
        finally:
            db.close()
    
    async def create_task(self, phone_number: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Todoist task"""
        try:
            token = self.get_user_token(phone_number)
            if not token:
                return {"success": False, "error": "User not authenticated with Todoist"}
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Prepare task payload
            task_payload = {
                "content": task_data.get('content', 'Meeting Reminder'),
                "description": task_data.get('description', ''),
                "priority": task_data.get('priority', 1),
            }
            
            # Add due date if provided
            if task_data.get('due_date'):
                if isinstance(task_data['due_date'], datetime):
                    task_payload['due_datetime'] = task_data['due_date'].isoformat()
                elif isinstance(task_data['due_date'], date):
                    task_payload['due_date'] = task_data['due_date'].isoformat()
            
            # Add labels if provided
            if task_data.get('labels'):
                task_payload['labels'] = task_data['labels']
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/tasks",
                    headers=headers,
                    json=task_payload
                )
                
                if response.status_code == 200:
                    task = response.json()
                    return {
                        "success": True,
                        "task_id": task['id'],
                        "task_url": task.get('url')
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Todoist API error: {response.status_code} - {response.text}"
                    }
                    
        except Exception as e:
            return {"success": False, "error": f"Todoist service error: {e}"}
    
    async def update_task(self, phone_number: str, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing Todoist task"""
        try:
            token = self.get_user_token(phone_number)
            if not token:
                return {"success": False, "error": "User not authenticated with Todoist"}
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/tasks/{task_id}",
                    headers=headers,
                    json=task_data
                )
                
                if response.status_code == 200:
                    return {"success": True}
                else:
                    return {
                        "success": False,
                        "error": f"Todoist API error: {response.status_code} - {response.text}"
                    }
                    
        except Exception as e:
            return {"success": False, "error": f"Todoist service error: {e}"}
    
    async def complete_task(self, phone_number: str, task_id: str) -> Dict[str, Any]:
        """Mark a Todoist task as completed"""
        try:
            token = self.get_user_token(phone_number)
            if not token:
                return {"success": False, "error": "User not authenticated with Todoist"}
            
            headers = {
                "Authorization": f"Bearer {token}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/tasks/{task_id}/close",
                    headers=headers
                )
                
                if response.status_code == 204:
                    return {"success": True}
                else:
                    return {
                        "success": False,
                        "error": f"Todoist API error: {response.status_code} - {response.text}"
                    }
                    
        except Exception as e:
            return {"success": False, "error": f"Todoist service error: {e}"}
    
    async def delete_task(self, phone_number: str, task_id: str) -> Dict[str, Any]:
        """Delete a Todoist task"""
        try:
            token = self.get_user_token(phone_number)
            if not token:
                return {"success": False, "error": "User not authenticated with Todoist"}
            
            headers = {
                "Authorization": f"Bearer {token}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/tasks/{task_id}",
                    headers=headers
                )
                
                if response.status_code == 204:
                    return {"success": True}
                else:
                    return {
                        "success": False,
                        "error": f"Todoist API error: {response.status_code} - {response.text}"
                    }
                    
        except Exception as e:
            return {"success": False, "error": f"Todoist service error: {e}"}

# Global instance
todoist_service = TodoistService()