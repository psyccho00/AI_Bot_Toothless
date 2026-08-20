from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Medication(Base):
    """Medication management model representing prescriptions, dosages, and compliance states"""
    __tablename__ = "medications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), index=True)
    
    # Medication details
    name = Column(String, index=True, nullable=False)
    dosage = Column(String, nullable=False)
    frequency = Column(String, nullable=False)  # once daily, twice daily, as needed, etc.
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    reason = Column(String, nullable=True)
    prescribed_by = Column(String, nullable=True)  # optional doctor or provider
    
    # Side effects and interactions
    known_side_effects = Column(Text, nullable=True)
    interactions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="medications")
