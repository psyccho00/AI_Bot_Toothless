from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class HealthProfile(Base):
    """Normalized health profiles containing demographics, contacts, avatars, and lifestyle metrics"""
    __tablename__ = "health_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, index=True)
    
    # Required demographics
    full_name = Column(String, nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String, nullable=False)
    
    # Required biometric indexes
    height = Column(Float, nullable=False)  # in cm
    weight = Column(Float, nullable=False)  # in kg
    
    # Optional parameters
    blood_group = Column(String, nullable=True)  # dropdown (A+, O-, etc)
    avatar = Column(String, nullable=True)       # pre-selected profile icon name
    
    # Emergency contact (Name, Relationship, Phone Number)
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_relationship = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)
    
    # Optional Profile Fields
    occupation = Column(String, nullable=True)
    smoking_status = Column(String, nullable=True)        # Yes, No, Former
    alcohol_consumption = Column(String, nullable=True)   # Non-drinker, Social, Regular
    exercise_frequency = Column(String, nullable=True)    # Rare, 1-2 times/week, 3+ times/week
    preferred_language = Column(String, nullable=True)    # English, Spanish, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="health_profile")
    conditions = relationship("MedicalCondition", back_populates="health_profile", cascade="all, delete-orphan")
    allergies = relationship("Allergy", back_populates="health_profile", cascade="all, delete-orphan")
    weight_histories = relationship("WeightHistory", back_populates="health_profile", cascade="all, delete-orphan")


class MedicalCondition(Base):
    """Individual diagnosed conditions containing severity, status, and diagnostic metadata"""
    __tablename__ = "medical_conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    health_profile_id = Column(Integer, ForeignKey("health_profiles.id"), index=True)
    
    condition_name = Column(String, index=True, nullable=False)
    diagnosed_date = Column(DateTime, nullable=True)
    severity = Column(String, nullable=True)        # Mild, Moderate, Severe
    is_resolved = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    health_profile = relationship("HealthProfile", back_populates="conditions")


class Allergy(Base):
    """Profile allergy records containing classification category tags"""
    __tablename__ = "allergies"
    
    id = Column(Integer, primary_key=True, index=True)
    health_profile_id = Column(Integer, ForeignKey("health_profiles.id"), index=True)
    
    allergy_name = Column(String, index=True, nullable=False)
    category = Column(String, nullable=True)        # Food, Medication, Environmental, Other
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    health_profile = relationship("HealthProfile", back_populates="allergies")


class WeightHistory(Base):
    """Chronological logging of weight measurements for future health analytics tracking"""
    __tablename__ = "weight_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    health_profile_id = Column(Integer, ForeignKey("health_profiles.id"), index=True)
    
    weight = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    health_profile = relationship("HealthProfile", back_populates="weight_histories")
