from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr


# ============ User Schemas ============
class UserBase(BaseModel):
    email: EmailStr
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
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Health Check-In Schemas ============
class HealthCheckInBase(BaseModel):
    symptoms: Optional[str] = None
    pain_level: Optional[int] = None
    energy_level: Optional[int] = None
    sleep_quality: Optional[int] = None
    sleep_hours: Optional[float] = None
    appetite: Optional[str] = None
    hydration_status: Optional[str] = None
    medication_compliance: bool = True
    notes: Optional[str] = None


class HealthCheckInCreate(HealthCheckInBase):
    pass


class HealthCheckInResponse(HealthCheckInBase):
    id: int
    user_id: int
    check_in_date: datetime
    ai_assessment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class HealthCheckInWithAI(HealthCheckInResponse):
    ai_assessment: str


# ============ Mood Entry Schemas ============
class MoodEntryBase(BaseModel):
    mood_rating: int
    mood_type: str
    stress_level: int
    anxiety_level: int
    depression_signs: int
    triggers: Optional[str] = None
    coping_strategies: Optional[str] = None
    notes: Optional[str] = None


class MoodEntryCreate(MoodEntryBase):
    pass


class MoodEntryResponse(MoodEntryBase):
    id: int
    user_id: int
    entry_date: datetime
    ai_recommendation: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Medication Schemas ============
class MedicationBase(BaseModel):
    name: str
    dosage: str
    frequency: str
    start_date: datetime
    end_date: Optional[datetime] = None
    reason: str
    known_side_effects: Optional[str] = None
    interactions: Optional[str] = None


class MedicationCreate(MedicationBase):
    pass


class MedicationUpdate(BaseModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    reason: Optional[str] = None
    end_date: Optional[datetime] = None
    known_side_effects: Optional[str] = None
    interactions: Optional[str] = None


class MedicationResponse(MedicationBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Medical Info Schemas ============
class MedicalInfoBase(BaseModel):
    condition_name: str
    description: str
    symptoms: str
    causes: str
    treatment_options: str
    when_to_see_doctor: str
    prevention_tips: str
    severity_level: str
    medical_sources: Optional[str] = None


class MedicalInfoCreate(MedicalInfoBase):
    pass


class MedicalInfoUpdate(BaseModel):
    description: Optional[str] = None
    symptoms: Optional[str] = None
    causes: Optional[str] = None
    treatment_options: Optional[str] = None
    when_to_see_doctor: Optional[str] = None
    prevention_tips: Optional[str] = None


class MedicalInfoResponse(MedicalInfoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Conversation Schemas ============
class ConversationMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ConversationBase(BaseModel):
    title: str
    topic: str
    messages: List[ConversationMessage]


class ConversationCreate(BaseModel):
    title: str
    topic: str
    initial_message: str


class ConversationUpdate(BaseModel):
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    topic: str
    messages: List[Dict[str, Any]]
    ai_summary: Optional[str] = None
    health_alerts: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Toothless AI Request/Response Schemas ============
class ToothlessRequest(BaseModel):
    user_id: int
    message: str
    context: Optional[str] = None
    include_recommendations: bool = True


class ToothlessResponse(BaseModel):
    response: str
    recommendations: Optional[List[str]] = None
    health_alerts: Optional[List[str]] = None
    follow_up_questions: Optional[List[str]] = None
    requires_professional_help: bool = False


class ToothlessDailyCheckIn(BaseModel):
    user_id: int


class ToothlessHealthAnalysis(BaseModel):
    user_id: int
    time_period_days: int = 7


# ============ Authentication Schemas ============
class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    username: str
    password: str


# ============ Health Dashboard Schemas ============
class HealthMetricsSummary(BaseModel):
    average_mood: float
    average_energy: float
    average_sleep: float
    mood_trend: str  # improving, declining, stable
    recent_symptoms: List[str]
    medication_compliance_rate: float
    entries_this_week: int


class HealthDashboard(BaseModel):
    user: UserResponse
    metrics: HealthMetricsSummary
    recent_checkings: List[HealthCheckInResponse]
    recent_mood_entries: List[MoodEntryResponse]
    active_medications: List[MedicationResponse]
    health_alerts: List[str]
