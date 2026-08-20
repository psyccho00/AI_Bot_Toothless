from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class MoodEntry(Base):
    """Mood tracking records capturing rating indexes, anxiety, depression signs, and coping triggers"""
    __tablename__ = "mood_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), index=True)
    entry_date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Mood metrics
    mood_rating = Column(Integer, nullable=False)       # 1-10 scale
    mood_type = Column(String, nullable=False)          # happy, sad, anxious, angry, neutral, etc.
    stress_level = Column(Integer, nullable=False)      # 1-10 scale
    anxiety_level = Column(Integer, nullable=False)     # 1-10 scale
    depression_signs = Column(Integer, nullable=False)  # 1-10 scale
    
    # Context
    triggers = Column(Text, nullable=True)
    coping_strategies = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    ai_recommendation = Column(Text, nullable=True)     # Toothless recommendation
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="mood_entries")
