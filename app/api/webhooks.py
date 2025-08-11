from fastapi import APIRouter, Request, HTTPException, Depends
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from app.core.config import get_settings
from app.services.ai_service import ai_service
from app.services.rag_service import rag_service
from app.services.scheduler import SchedulerService
import logging

settings = get_settings()
router = APIRouter()
logger = logging.getLogger(__name__)

def validate_twilio_request(request: Request):
    """Validate that the request is from Twilio"""
    validator = RequestValidator(settings.twilio_auth_token)
    
    # Get the URL and signature
    url = str(request.url)
    signature = request.headers.get('X-Twilio-Signature', '')
    
    # This would need the actual form data for validation
    # For now, we'll skip validation in development
    if not settings.debug:
        # In production, implement proper validation
        pass
    
    return True

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages"""
    
    try:
        # Validate request (implement properly in production)
        validate_twilio_request(request)
        
        # Parse form data
        form_data = await request.form()
        
        # Extract message details
        from_number = form_data.get('From', '')
        message_body = form_data.get('Body', '')
        
        logger.info(f"Received message from {from_number}: {message_body}")
        
        # Process the message
        response_text = await process_whatsapp_message(from_number, message_body)
        
        # Create Twilio response
        resp = MessagingResponse()
        resp.message(response_text)
        
        return str(resp)
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        resp = MessagingResponse()
        resp.message("Sorry, I encountered an error. Please try again later.")
        return str(resp)

async def process_whatsapp_message(from_number: str, message: str) -> str:
    """Process incoming WhatsApp message and return response"""
    
    try:
        # Clean phone number (remove whatsapp: prefix)
        phone = from_number.replace('whatsapp:', '')
        
        # Get enhanced context using RAG
        enhanced_context = rag_service.enhance_ai_context(phone, message)
        
        # Use AI to classify intent and extract information
        ai_result = ai_service.classify_intent(message)
        
        logger.info(f"AI result: {ai_result}")
        
        # Store conversation context for future reference
        rag_service.store_conversation_context(phone, message, ai_result)
        
        # Handle different intents
        intent = ai_result.get('intent')
        
        if intent == 'schedule':
            return await handle_schedule_request(phone, ai_result, enhanced_context)
        elif intent == 'cancel':
            return await handle_cancel_request(phone, ai_result, enhanced_context)
        elif intent == 'reschedule':
            return await handle_reschedule_request(phone, ai_result, enhanced_context)
        elif intent == 'info':
            return await handle_info_request(phone, ai_result, enhanced_context)
        else:
            # Use RAG to generate contextual response
            return rag_service.generate_contextual_response(enhanced_context)
    
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return "I'm having trouble understanding that. Could you please rephrase your request?"

async def handle_schedule_request(phone: str, ai_result: dict, enhanced_context: dict) -> str:
    """Handle scheduling requests"""
    
    # Check if we have enough information
    required_fields = ['date', 'time']
    missing_fields = [field for field in required_fields if not ai_result.get(field)]
    
    if missing_fields:
        # Use RAG context to provide personalized response
        if enhanced_context.get('meeting_history'):
            return f"I'd be happy to schedule that meeting! Based on your usual preferences, could you please provide the {', '.join(missing_fields)}?"
        else:
            return f"I'd be happy to schedule that meeting! Could you please provide the {', '.join(missing_fields)}?"
    
    # Initialize scheduler service
    scheduler = SchedulerService()
    
    try:
        # Create the meeting
        result = await scheduler.create_meeting(phone, ai_result)
        
        if result['success']:
            meeting_type = ai_result.get('meeting_type', 'meeting')
            location_text = f" at {ai_result['location']}" if ai_result.get('location') else ""
            
            return f"✅ Perfect! I've scheduled your {meeting_type} for {ai_result['date']} at {ai_result['time']}{location_text}. You'll see it in Google Calendar and get a Todoist reminder on the day."
        else:
            return f"❌ Sorry, I couldn't create the meeting: {result['error']}"
            
    except Exception as e:
        logger.error(f"Scheduling error: {e}")
        return "I encountered an issue while scheduling. Please try again."

async def handle_cancel_request(phone: str, ai_result: dict, enhanced_context: dict) -> str:
    """Handle cancellation requests"""
    # Check recent meetings for context
    recent_meetings = enhanced_context.get('meeting_history', [])
    
    if recent_meetings:
        upcoming_meetings = [m for m in recent_meetings if m['status'] == 'scheduled']
        if upcoming_meetings:
            meeting_list = "\n".join([f"• {m['title']} on {m['start_time'][:10]}" for m in upcoming_meetings[:3]])
            return f"I can help you cancel a meeting. Here are your upcoming meetings:\n\n{meeting_list}\n\nWhich one would you like to cancel?"
    
    return "I'll help you cancel a meeting. Could you tell me which meeting you'd like to cancel?"

async def handle_reschedule_request(phone: str, ai_result: dict, enhanced_context: dict) -> str:
    """Handle rescheduling requests"""
    # Check recent meetings for context
    recent_meetings = enhanced_context.get('meeting_history', [])
    
    if recent_meetings:
        upcoming_meetings = [m for m in recent_meetings if m['status'] == 'scheduled']
        if upcoming_meetings:
            meeting_list = "\n".join([f"• {m['title']} on {m['start_time'][:10]}" for m in upcoming_meetings[:3]])
            return f"I can help you reschedule a meeting. Here are your upcoming meetings:\n\n{meeting_list}\n\nWhich one would you like to reschedule, and what's the new time?"
    
    return "I'll help you reschedule. Which meeting would you like to move, and what's the new time?"

async def handle_info_request(phone: str, ai_result: dict, enhanced_context: dict) -> str:
    """Handle information requests"""
    # Provide meeting information based on context
    recent_meetings = enhanced_context.get('meeting_history', [])
    
    if recent_meetings:
        upcoming_meetings = [m for m in recent_meetings if m['status'] == 'scheduled']
        if upcoming_meetings:
            meeting_list = "\n".join([
                f"📅 {m['title']}\n   {m['start_time'][:16]} - {m['location'] or 'No location'}"
                for m in upcoming_meetings[:5]
            ])
            return f"Here are your upcoming meetings:\n\n{meeting_list}\n\nNeed help with any of these?"
        else:
            return "You don't have any upcoming meetings scheduled. Would you like to schedule one?"
    else:
        return "I don't see any meetings in your history yet. Would you like to schedule your first meeting?"

def generate_help_response() -> str:
    """Generate help response"""
    return """
Hi! I'm your scheduling assistant 🤖

I can help you:
📅 Schedule meetings: "Let's meet Tuesday at 3pm"
❌ Cancel meetings: "Cancel my meeting with John"
🔄 Reschedule meetings: "Move tomorrow's meeting to Friday"
ℹ️ Get meeting info: "What meetings do I have this week?"

Just send me a message in natural language!
    """.strip()