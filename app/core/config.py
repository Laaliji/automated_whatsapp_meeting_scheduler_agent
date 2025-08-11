from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_whatsapp_number: str
    
    # Google OAuth
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    
    # Todoist OAuth
    todoist_client_id: str
    todoist_client_secret: str
    
    # Database
    database_url: str = "sqlite:///./scheduler.db"
    redis_url: str = "redis://localhost:6379"
    
    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    
    # App
    secret_key: str
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()