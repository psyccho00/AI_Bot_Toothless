from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User model for storing patient information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    age = Column(Integer)
    gender = Column(String)
    medical_history = Column(Text, nullable=True)
    allergies = Column(Text, nullable=True)
    current_medications = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    health_checkings = relationship("HealthCheckIn", back_populates="user", cascade="all, delete-orphan")
    mood_entries = relationship("MoodEntry", back_populates="user", cascade="all, delete-orphan")
    medications = relationship("Medication", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class HealthCheckIn(Base):
    """Daily health check-in records"""
    __tablename__ = "health_check_ins"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    check_in_date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Health metrics
    symptoms = Column(Text, nullable=True)
    pain_level = Column(Integer, nullable=True)  # 0-10 scale
    energy_level = Column(Integer, nullable=True)  # 0-10 scale
    sleep_quality = Column(Integer, nullable=True)  # 0-10 scale
    sleep_hours = Column(Float, nullable=True)
    appetite = Column(String, nullable=True)  # poor, normal, good
    hydration_status = Column(String, nullable=True)  # low, adequate, good
    medication_compliance = Column(Boolean, default=True)
    
    # Additional notes
    notes = Column(Text, nullable=True)
    ai_assessment = Column(Text, nullable=True)  # Toothless AI assessment
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="health_checkings")


class MoodEntry(Base):
    """Mood tracking entries"""
    __tablename__ = "mood_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    entry_date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Mood metrics
    mood_rating = Column(Integer)  # 1-10 scale
    mood_type = Column(String)  # happy, sad, anxious, angry, neutral, etc.
    stress_level = Column(Integer)  # 1-10 scale
    anxiety_level = Column(Integer)  # 1-10 scale
    depression_signs = Column(Integer)  # 1-10 scale
    
    # Context
    triggers = Column(Text, nullable=True)
    coping_strategies = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    ai_recommendation = Column(Text, nullable=True)  # Toothless recommendation
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="mood_entries")


class Medication(Base):
    """Medication management"""
    __tablename__ = "medications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Medication details
    name = Column(String, index=True)
    dosage = Column(String)
    frequency = Column(String)  # once daily, twice daily, as needed, etc.
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    reason = Column(String)
    
    # Side effects and interactions
    known_side_effects = Column(Text, nullable=True)
    interactions = Column(Text, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="medications")


class MedicalInfo(Base):
    """Medical information and conditions"""
    __tablename__ = "medical_info"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Condition details
    condition_name = Column(String, index=True)
    description = Column(Text)
    symptoms = Column(Text)
    causes = Column(Text)
    treatment_options = Column(Text)
    when_to_see_doctor = Column(Text)
    prevention_tips = Column(Text)
    severity_level = Column(String)  # mild, moderate, severe
    
    # References
    medical_sources = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Conversation(Base):
    """Conversation history with Toothless AI"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Conversation details
    title = Column(String)
    topic = Column(String)  # health_checkin, mood_tracking, medical_info, general, etc.
    
    # Message history
    messages = Column(JSON)  # Stores conversation history as JSON
    
    # Assessment
    ai_summary = Column(Text, nullable=True)
    health_alerts = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="conversations")
