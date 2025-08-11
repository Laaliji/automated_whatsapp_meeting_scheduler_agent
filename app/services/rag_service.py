import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI
from app.core.config import get_settings
from app.models.database import SessionLocal, Conversation, Meeting, User

settings = get_settings()

class RAGService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.qdrant_client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key if settings.qdrant_api_key else None
        )
        self.collection_name = "conversation_context"
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure the Qdrant collection exists"""
        try:
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
                )
        except Exception as e:
            print(f"Error ensuring collection: {e}")
    
    def get_embedding(self, text: str) -> List[float]:
        """Get OpenAI embedding for text"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return []
    
    def store_conversation_context(self, phone_number: str, message: str, context: Dict[str, Any]):
        """Store conversation context in vector database"""
        try:
            # Create searchable text
            searchable_text = f"User: {phone_number}\nMessage: {message}\nContext: {json.dumps(context)}"
            
            # Get embedding
            embedding = self.get_embedding(searchable_text)
            if not embedding:
                return
            
            # Create point
            point = PointStruct(
                id=hash(f"{phone_number}_{datetime.now().isoformat()}"),
                vector=embedding,
                payload={
                    "phone_number": phone_number,
                    "message": message,
                    "context": context,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Store in Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
        except Exception as e:
            print(f"Error storing context: {e}")
    
    def get_relevant_context(self, phone_number: str, message: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant conversation context"""
        try:
            # Get embedding for current message
            embedding = self.get_embedding(message)
            if not embedding:
                return []
            
            # Search for similar contexts
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=embedding,
                query_filter={
                    "must": [
                        {"key": "phone_number", "match": {"value": phone_number}}
                    ]
                },
                limit=limit
            )
            
            # Extract relevant contexts
            contexts = []
            for result in search_result:
                contexts.append({
                    "message": result.payload["message"],
                    "context": result.payload["context"],
                    "timestamp": result.payload["timestamp"],
                    "score": result.score
                })
            
            return contexts
            
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return []
    
    def get_user_meeting_history(self, phone_number: str, days_back: int = 30) -> List[Dict[str, Any]]:
        """Get user's recent meeting history"""
        db = SessionLocal()
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            meetings = db.query(Meeting).join(User).filter(
                User.phone_number == phone_number,
                Meeting.created_at >= cutoff_date
            ).order_by(Meeting.start_time.desc()).limit(10).all()
            
            meeting_history = []
            for meeting in meetings:
                meeting_history.append({
                    "title": meeting.title,
                    "start_time": meeting.start_time.isoformat(),
                    "end_time": meeting.end_time.isoformat(),
                    "location": meeting.location,
                    "meeting_type": meeting.meeting_type,
                    "status": meeting.status
                })
            
            return meeting_history
            
        finally:
            db.close()
    
    def enhance_ai_context(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Enhance AI context with RAG information"""
        try:
            # Get relevant conversation context
            conversation_context = self.get_relevant_context(phone_number, message)
            
            # Get meeting history
            meeting_history = self.get_user_meeting_history(phone_number)
            
            # Get current conversation state
            db = SessionLocal()
            try:
                conversation = db.query(Conversation).filter(
                    Conversation.user_phone == phone_number
                ).first()
                
                current_context = conversation.context if conversation else {}
            finally:
                db.close()
            
            # Build enhanced context
            enhanced_context = {
                "current_message": message,
                "conversation_history": conversation_context,
                "meeting_history": meeting_history,
                "current_context": current_context,
                "user_phone": phone_number,
                "timestamp": datetime.now().isoformat()
            }
            
            return enhanced_context
            
        except Exception as e:
            print(f"Error enhancing context: {e}")
            return {"current_message": message, "user_phone": phone_number}
    
    def generate_contextual_response(self, enhanced_context: Dict[str, Any]) -> str:
        """Generate response using enhanced RAG context"""
        try:
            prompt = f"""
            You are an intelligent scheduling assistant with access to conversation history and meeting patterns.
            
            Current message: "{enhanced_context['current_message']}"
            
            User's recent meetings:
            {json.dumps(enhanced_context.get('meeting_history', []), indent=2)}
            
            Recent conversation context:
            {json.dumps(enhanced_context.get('conversation_history', []), indent=2)}
            
            Current conversation state:
            {json.dumps(enhanced_context.get('current_context', {}), indent=2)}
            
            Based on this context, provide a helpful and personalized response. Consider:
            - User's meeting patterns and preferences
            - Previous conversation context
            - Any ongoing scheduling discussions
            - Be natural and conversational
            - Reference relevant past interactions when helpful
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful scheduling assistant with memory of past interactions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating contextual response: {e}")
            return "I'm here to help with your scheduling needs. What would you like to do?"

# Global instance
rag_service = RAGService()