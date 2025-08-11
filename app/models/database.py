from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    google_refresh_token = Column(Text)
    todoist_token = Column(String)
    preferences = Column(JSON, default={})
    timezone = Column(String, default="UTC")
    created_at = Column(DateTime, default=datetime.utcnow)

class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    google_event_id = Column(String)
    todoist_task_id = Column(String)
    title = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    location = Column(String)
    meeting_type = Column(String)  # virtual/in-person
    status = Column(String, default="scheduled")  # scheduled/completed/cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_phone = Column(String, index=True)
    context = Column(JSON, default={})
    last_message = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)