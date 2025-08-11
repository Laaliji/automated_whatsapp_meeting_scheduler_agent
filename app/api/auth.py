from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from app.core.config import get_settings
from app.models.database import SessionLocal, User
import httpx
import logging

settings = get_settings()
router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/auth/google")
async def google_auth_start(phone: str = Query(...)):
    """Start Google OAuth flow"""
    try:
        # Create flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.google_redirect_uri]
                }
            },
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        
        flow.redirect_uri = settings.google_redirect_uri
        
        # Generate authorization URL
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=phone  # Pass phone number in state
        )
        
        return RedirectResponse(url=authorization_url)
        
    except Exception as e:
        logger.error(f"Google auth start error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start Google authentication")

@router.get("/auth/google/callback")
async def google_auth_callback(code: str = Query(...), state: str = Query(...)):
    """Handle Google OAuth callback"""
    try:
        phone = state  # Phone number passed in state
        
        # Create flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.google_redirect_uri]
                }
            },
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        
        flow.redirect_uri = settings.google_redirect_uri
        
        # Exchange code for tokens
        flow.fetch_token(code=code)
        
        # Store refresh token
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.phone_number == phone).first()
            if not user:
                user = User(phone_number=phone)
                db.add(user)
            
            user.google_refresh_token = flow.credentials.refresh_token
            db.commit()
            
            return {"message": "Google Calendar connected successfully! You can now schedule meetings."}
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Google auth callback error: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete Google authentication")

@router.get("/auth/todoist")
async def todoist_auth_start(phone: str = Query(...)):
    """Start Todoist OAuth flow"""
    try:
        # Todoist OAuth URL
        auth_url = f"https://todoist.com/oauth/authorize?client_id={settings.todoist_client_id}&scope=data:read_write&state={phone}"
        
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        logger.error(f"Todoist auth start error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start Todoist authentication")

@router.get("/auth/todoist/callback")
async def todoist_auth_callback(code: str = Query(...), state: str = Query(...)):
    """Handle Todoist OAuth callback"""
    try:
        phone = state  # Phone number passed in state
        
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://todoist.com/oauth/access_token",
                data={
                    "client_id": settings.todoist_client_id,
                    "client_secret": settings.todoist_client_secret,
                    "code": code
                }
            )
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data["access_token"]
                
                # Store token
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.phone_number == phone).first()
                    if not user:
                        user = User(phone_number=phone)
                        db.add(user)
                    
                    user.todoist_token = access_token
                    db.commit()
                    
                    return {"message": "Todoist connected successfully! You'll now get task reminders for your meetings."}
                    
                finally:
                    db.close()
            else:
                raise HTTPException(status_code=400, detail="Failed to get Todoist access token")
                
    except Exception as e:
        logger.error(f"Todoist auth callback error: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete Todoist authentication")

@router.get("/auth/status/{phone}")
async def auth_status(phone: str):
    """Check authentication status for a user"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.phone_number == phone).first()
        
        if not user:
            return {
                "google_connected": False,
                "todoist_connected": False,
                "message": "User not found"
            }
        
        return {
            "google_connected": bool(user.google_refresh_token),
            "todoist_connected": bool(user.todoist_token),
            "message": "Authentication status retrieved"
        }
        
    finally:
        db.close()