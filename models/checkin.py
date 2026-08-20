from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class HealthCheckIn(Base):
    """Daily health check-in records containing symptoms, pain, sleep quality, and medication compliance states"""
    __tablename__ = "health_check_ins"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), index=True)
    check_in_date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Health metrics
    symptoms = Column(Text, nullable=True)
    pain_level = Column(Integer, nullable=True)      # 0-10 scale
    energy_level = Column(Integer, nullable=True)    # 0-10 scale
    sleep_quality = Column(Integer, nullable=True)   # 0-10 scale
    sleep_hours = Column(Float, nullable=True)
    appetite = Column(String, nullable=True)          # poor, normal, good
    hydration_status = Column(String, nullable=True)  # low, adequate, good
    medication_compliance = Column(Boolean, default=True)
    
    # Additional notes
    notes = Column(Text, nullable=True)
    ai_assessment = Column(Text, nullable=True)       # Toothless AI assessment
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="health_checkings")
