from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr

# Profile Creation Schema
class ProfileCreate(BaseModel):
    username: str                     # Profile display name (unique username)
    password: str                     # 4-digit PIN or password
    full_name: str
    date_of_birth: date               # YYYY-MM-DD
    gender: str
    height: float                     # cm
    weight: float                     # kg
    blood_group: Optional[str] = None
    avatar: Optional[str] = None      # Avatar identifier emoji
    
    # Emergency Contact
    emergency_contact_name: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    
    # Optional fields
    occupation: Optional[str] = None
    smoking_status: Optional[str] = None
    alcohol_consumption: Optional[str] = None
    exercise_frequency: Optional[str] = None
    preferred_language: Optional[str] = None
    
    # Initial health info (comma-separated strings)
    allergies: Optional[str] = None
    allergies_categories: Optional[str] = None # Matching comma-separated category names
    existing_conditions: Optional[str] = None
    current_medications: Optional[str] = None

# Profile Updates Schema
class ProfileUpdateRequest(BaseModel):
    weight: float
    height: float
    emergency_contact_name: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    
    # Optional metrics updates
    occupation: Optional[str] = None
    smoking_status: Optional[str] = None
    alcohol_consumption: Optional[str] = None
    exercise_frequency: Optional[str] = None
    preferred_language: Optional[str] = None
    
    # Comma-separated strings for overwrite sync
    medications: Optional[str] = None
    conditions: Optional[str] = None
    allergies: Optional[str] = None
    allergies_categories: Optional[str] = None

# Authentication Request Schemas
class ProfileLoginRequest(BaseModel):
    pin: str

class RememberMeLoginRequest(BaseModel):
    user_id: str
    token: str

# Weight History response sub-model
class WeightHistoryResponse(BaseModel):
    weight: float
    recorded_at: datetime
    
    class Config:
        from_attributes = True

# Profile Detail Response Schema
class ProfileDetailResponse(BaseModel):
    id: str
    username: str
    full_name: str
    date_of_birth: date
    age: int
    gender: str
    height: float
    weight: float
    blood_group: Optional[str] = None
    avatar: Optional[str] = None
    last_login: Optional[datetime] = None
    
    # Emergency Contact
    emergency_contact_name: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    
    # Optional metadata
    occupation: Optional[str] = None
    smoking_status: Optional[str] = None
    alcohol_consumption: Optional[str] = None
    exercise_frequency: Optional[str] = None
    preferred_language: Optional[str] = None
    
    # Normalized list details
    conditions: str
    allergies: str
    medications: str
    
    # Weight trend list
    weight_history: List[WeightHistoryResponse]
    
    class Config:
        from_attributes = True

# Profile Short Response Schema (Selection Grid)
class ProfileSelectionResponse(BaseModel):
    id: str
    username: str
    full_name: str
    avatar: Optional[str] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Standard legacy schemas for compatibility
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: str
    full_name: str
    age: int
    gender: str
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None

class UserResponse(UserBase):
    id: str  # Updated to str to support UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
