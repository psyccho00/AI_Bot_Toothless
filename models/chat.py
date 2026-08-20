from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base

class Conversation(Base):
    """Conversation history with Toothless AI capturing summaries, prompts list, and health alerts metadata"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), index=True)
    
    # Conversation details
    title = Column(String, nullable=False)
    topic = Column(String, nullable=False)  # health_checkin, mood_tracking, medical_info, general, etc.
    
    # Message history
    messages = Column(JSON, nullable=False)  # Stores conversation history as JSON list
    
    # Assessment
    ai_summary = Column(Text, nullable=True)
    health_alerts = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="conversations")
