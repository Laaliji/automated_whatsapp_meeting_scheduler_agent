import json
from typing import Dict, Any, Optional
from openai import OpenAI
from app.core.config import get_settings

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)

class AIService:
    def __init__(self):
        self.client = client
    
    def classify_intent(self, message: str) -> Dict[str, Any]:
        """Classify user intent and extract scheduling information"""
        
        prompt = f"""
        Analyze this WhatsApp message and extract scheduling information in JSON format.
        
        Message: "{message}"
        
        Extract:
        {{
            "intent": "schedule|cancel|reschedule|info|other",
            "date": "YYYY-MM-DD or null",
            "time": "HH:MM or null", 
            "timezone": "timezone or null",
            "duration_minutes": number or null,
            "meeting_type": "virtual|in-person or null",
            "location": "location string or null",
            "participants": ["email1", "email2"] or null,
            "title": "meeting title or null",
            "confidence": 0.0-1.0
        }}
        
        Rules:
        - If date is relative (like "tomorrow", "next week"), convert to actual date
        - Default duration is 30 minutes if not specified
        - Use Casablanca timezone if not specified
        - Set confidence based on how clear the request is
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a scheduling assistant. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"AI Service error: {e}")
            return {
                "intent": "other",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def generate_response(self, context: Dict[str, Any]) -> str:
        """Generate a natural response based on context"""
        
        prompt = f"""
        Generate a natural WhatsApp response based on this context:
        
        Context: {json.dumps(context, indent=2)}
        
        Guidelines:
        - Be friendly and conversational
        - Confirm important details
        - Ask for missing information if needed
        - Use emojis sparingly
        - Keep responses concise but helpful
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful scheduling assistant. Be natural and friendly."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Sorry, I had trouble processing that. Can you please try again? Error: {str(e)}"

# Global instance
ai_service = AIService()