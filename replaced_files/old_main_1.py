from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import json




from config import settings
from database import get_db, init_db
from schemas import (
    UserCreate, UserResponse, UserUpdate,
    HealthCheckInCreate, HealthCheckInResponse, HealthCheckInWithAI,
    MoodEntryCreate, MoodEntryResponse,
    MedicationCreate, MedicationResponse, MedicationUpdate,
    MedicalInfoCreate, MedicalInfoResponse,
    ConversationCreate, ConversationResponse,
    ToothlessRequest, ToothlessResponse,
    LoginRequest, TokenResponse,
    HealthDashboard, HealthMetricsSummary
)
from models import (
    User, HealthCheckIn, MoodEntry, Medication,
    MedicalInfo, Conversation
)
from toothless_ai import toothless
import models

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Toothless - Your AI Health Assistant"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Startup Events ====================
@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✅ Database initialized")
    print(f"🐉 Welcome to {settings.APP_NAME}!")


# ==================== Health Check ====================
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# ==================== User Management ====================
@app.post("/users/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    db_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    # Create new user
    new_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        age=user.age,
        gender=user.gender,
        medical_history=user.medical_history,
        allergies=user.allergies,
        current_medications=user.current_medications,
        hashed_password=user.password  # In production, hash this!
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@app.post("/users/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or user.hashed_password != login_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # In production, create a proper JWT token
    return {
        "access_token": f"token_user_{user.id}",
        "token_type": "bearer"
    }


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user details"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update user details"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_update.full_name:
        user.full_name = user_update.full_name
    if user_update.age:
        user.age = user_update.age
    if user_update.medical_history:
        user.medical_history = user_update.medical_history
    if user_update.allergies:
        user.allergies = user_update.allergies
    if user_update.current_medications:
        user.current_medications = user_update.current_medications
    
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    return user


# ==================== Health Check-Ins ====================
@app.post("/health-checkins", response_model=HealthCheckInWithAI)
def create_health_checkin(checkin: HealthCheckInCreate, user_id: int, db: Session = Depends(get_db)):
    """Create a new health check-in with Toothless AI assessment"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get AI assessment
    checkin_context = f"""
    Health Check-In Data:
    - Symptoms: {checkin.symptoms}
    - Pain Level: {checkin.pain_level}/10
    - Energy Level: {checkin.energy_level}/10
    - Sleep Quality: {checkin.sleep_quality}/10
    - Sleep Hours: {checkin.sleep_hours}
    - Appetite: {checkin.appetite}
    - Hydration: {checkin.hydration_status}
    - Medication Compliance: {checkin.medication_compliance}
    """
    
    # ai_response = toothless.chat(
    #     user_id=user_id,
    #     user_message=f"I'm having: {checkin.symptoms or 'no specific symptoms'}. Pain: {checkin.pain_level or 'none'}, Energy: {checkin.energy_level}, Sleep: {checkin.sleep_hours}h",
    #     context=checkin_context
    # )

    import logging

    try:
        ai_response = toothless.chat(
            user_id=user_id,
            user_message=f"I'm having: {checkin.symptoms or 'no symptoms'}",
            context=checkin_context
        )
    except Exception as e:
        # logging.error(f"AI ERROR: {e}")
        logging.exception("AI ERROR occurred during health check-in")
        ai_response = {"response": "AI unavailable at the moment."}

    
    # Create check-in record
    # db_checkin = HealthCheckIn(
    db_checkin = models.HealthCheckIn(
        user_id=user_id,
        symptoms=checkin.symptoms,
        pain_level=checkin.pain_level,
        energy_level=checkin.energy_level,
        sleep_quality=checkin.sleep_quality,
        sleep_hours=checkin.sleep_hours,
        appetite=checkin.appetite,
        hydration_status=checkin.hydration_status,
        medication_compliance=checkin.medication_compliance,
        notes=checkin.notes,
        # ai_assessment=ai_response["response"]
        ai_assessment=ai_response.get("response", str(ai_response))
    )
    
    db.add(db_checkin)
    db.commit()
    db.refresh(db_checkin)
    
    return db_checkin


@app.get("/health-checkins/{user_id}", response_model=List[HealthCheckInResponse])
def get_user_checkins(user_id: int, days: int = 7, db: Session = Depends(get_db)):
    """Get user's recent health check-ins"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    checkins = db.query(HealthCheckIn).filter(
        (HealthCheckIn.user_id == user_id) &
        (HealthCheckIn.created_at >= cutoff_date)
    ).order_by(HealthCheckIn.created_at.desc()).all()
    
    return checkins


# ==================== Mood Tracking ====================
@app.post("/mood-entries", response_model=MoodEntryResponse)
def create_mood_entry(mood: MoodEntryCreate, user_id: int, db: Session = Depends(get_db)):
    """Create a mood entry with Toothless AI recommendation"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get AI recommendation
    # mood_analysis = toothless.analyze_mood(user_id, mood.dict())

    try:
        mood_analysis = toothless.analyze_mood(user_id, mood.dict())
    except Exception:
        logging.exception("AI ERROR occurred during mood analysis")
        mood_analysis = {"response": "AI unavailable at the moment."}

    # Create mood entry
    # db_mood = MoodEntry(
    db_mood=models.MoodEntry(
        user_id=user_id,
        mood_rating=mood.mood_rating,
        mood_type=mood.mood_type,
        stress_level=mood.stress_level,
        anxiety_level=mood.anxiety_level,
        depression_signs=mood.depression_signs,
        triggers=mood.triggers,
        coping_strategies=mood.coping_strategies,
        notes=mood.notes,
        # ai_recommendation=mood_analysis["mood_analysis"]
        # ai_recommendation = mood_analysis.get("response", str(mood_analysis))
        ai_recommendation=mood_analysis.get(
            "response",
            mood_analysis.get("mood_analysis", str(mood_analysis))
        )
    )
    
    db.add(db_mood)
    db.commit()
    db.refresh(db_mood)
    
    return db_mood


@app.get("/mood-entries/{user_id}", response_model=List[MoodEntryResponse])
def get_mood_entries(user_id: int, days: int = 7, db: Session = Depends(get_db)):
    """Get user's recent mood entries"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    entries = db.query(MoodEntry).filter(
        (MoodEntry.user_id == user_id) &
        (MoodEntry.created_at >= cutoff_date)
    ).order_by(MoodEntry.created_at.desc()).all()
    
    return entries


# ==================== Medication Management ====================
@app.post("/medications", response_model=MedicationResponse)
def add_medication(med: MedicationCreate, user_id: int, db: Session = Depends(get_db)):
    """Add a new medication for the user"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db_med = Medication(
        user_id=user_id,
        name=med.name,
        dosage=med.dosage,
        frequency=med.frequency,
        start_date=med.start_date,
        end_date=med.end_date,
        reason=med.reason,
        known_side_effects=med.known_side_effects,
        interactions=med.interactions
    )
    
    db.add(db_med)
    db.commit()
    db.refresh(db_med)
    
    return db_med


@app.get("/medications/{user_id}", response_model=List[MedicationResponse])
def get_user_medications(user_id: int, db: Session = Depends(get_db)):
    """Get user's medications"""
    medications = db.query(Medication).filter(
        (Medication.user_id == user_id) &
        (Medication.is_active == True)
    ).all()
    
    return medications


@app.put("/medications/{medication_id}", response_model=MedicationResponse)
def update_medication(medication_id: int, med_update: MedicationUpdate, db: Session = Depends(get_db)):
    """Update medication information"""
    medication = db.query(Medication).filter(Medication.id == medication_id).first()
    
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )
    
    if med_update.name:
        medication.name = med_update.name
    if med_update.dosage:
        medication.dosage = med_update.dosage
    if med_update.frequency:
        medication.frequency = med_update.frequency
    if med_update.reason:
        medication.reason = med_update.reason
    if med_update.end_date:
        medication.end_date = med_update.end_date
    
    medication.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(medication)
    
    return medication


# ==================== Medical Information ====================
@app.post("/medical-info", response_model=MedicalInfoResponse)
def create_medical_info(info: MedicalInfoCreate, db: Session = Depends(get_db)):
    """Add medical information/condition"""
    db_info = MedicalInfo(
        condition_name=info.condition_name,
        description=info.description,
        symptoms=info.symptoms,
        causes=info.causes,
        treatment_options=info.treatment_options,
        when_to_see_doctor=info.when_to_see_doctor,
        prevention_tips=info.prevention_tips,
        severity_level=info.severity_level,
        medical_sources=info.medical_sources
    )
    
    db.add(db_info)
    db.commit()
    db.refresh(db_info)
    
    return db_info


@app.get("/medical-info/{condition_name}", response_model=MedicalInfoResponse)
def get_medical_info(condition_name: str, db: Session = Depends(get_db)):
    """Get medical information about a condition"""
    info = db.query(MedicalInfo).filter(
        MedicalInfo.condition_name.ilike(f"%{condition_name}%")
    ).first()
    
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical information not found"
        )
    
    return info


# ==================== Toothless AI Conversations ====================
@app.post("/toothless/chat", response_model=ToothlessResponse)
def chat_with_toothless(request: ToothlessRequest, db: Session = Depends(get_db)):
    """Chat with Toothless AI"""
    user = db.query(User).filter(User.id == request.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Build user context
    context = f"""
    User: {user.full_name}, Age: {user.age}, Gender: {user.gender}
    Medical History: {user.medical_history or 'None reported'}
    Allergies: {user.allergies or 'None reported'}
    Current Medications: {user.current_medications or 'None reported'}
    """
    
    # Get response from Toothless
    response = toothless.chat(
        user_id=request.user_id,
        user_message=request.message,
        context=context if request.context is None else request.context
    )
    
    # Store conversation
    conversation = db.query(Conversation).filter(
        Conversation.user_id == request.user_id
    ).order_by(Conversation.created_at.desc()).first()
    
    if not conversation:
        conversation = Conversation(
            user_id=request.user_id,
            title="Health Assistant Chat",
            topic="general",
            messages=json.dumps([])
        )
        db.add(conversation)
    
    # Update messages
    messages = json.loads(conversation.messages) if isinstance(conversation.messages, str) else conversation.messages or []
    messages.append({"role": "user", "content": request.message, "timestamp": datetime.utcnow().isoformat()})
    messages.append({"role": "assistant", "content": response["response"], "timestamp": datetime.utcnow().isoformat()})
    
    conversation.messages = json.dumps(messages)
    conversation.updated_at = datetime.utcnow()
    
    db.commit()
    
    return ToothlessResponse(
        response=response["response"],
        recommendations=response.get("follow_up_questions", []),
        health_alerts=response.get("health_alerts", []),
        requires_professional_help=response.get("requires_professional_help", False)
    )


@app.post("/toothless/daily-checkin")
def daily_checkin(user_id: int, db: Session = Depends(get_db)):
    """Start a daily health check-in with Toothless"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    checkin = toothless.daily_health_checkin(
        user_id=user_id,
        user_profile={
            "full_name": user.full_name,
            "age": user.age,
            "gender": user.gender,
            "medical_history": user.medical_history,
            "allergies": user.allergies,
            "current_medications": user.current_medications
        }
    )
    
    return checkin


@app.get("/toothless/conversations/{user_id}", response_model=List[ConversationResponse])
def get_conversations(user_id: int, db: Session = Depends(get_db)):
    """Get user's conversations with Toothless"""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).order_by(Conversation.created_at.desc()).all()
    
    return conversations


# ==================== Health Dashboard ====================
@app.get("/dashboard/{user_id}", response_model=HealthDashboard)
def get_health_dashboard(user_id: int, days: int = 7, db: Session = Depends(get_db)):
    """Get comprehensive health dashboard"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get recent data
    recent_checkins = db.query(HealthCheckIn).filter(
        (HealthCheckIn.user_id == user_id) &
        (HealthCheckIn.created_at >= cutoff_date)
    ).order_by(HealthCheckIn.created_at.desc()).limit(7).all()
    
    recent_moods = db.query(MoodEntry).filter(
        (MoodEntry.user_id == user_id) &
        (MoodEntry.created_at >= cutoff_date)
    ).order_by(MoodEntry.created_at.desc()).limit(7).all()
    
    active_meds = db.query(Medication).filter(
        (Medication.user_id == user_id) &
        (Medication.is_active == True)
    ).all()
    
    # Calculate metrics
    avg_mood = sum([m.mood_rating for m in recent_moods]) / len(recent_moods) if recent_moods else 0
    avg_energy = sum([c.energy_level for c in recent_checkins if c.energy_level]) / len([c for c in recent_checkins if c.energy_level]) if recent_checkins else 0
    avg_sleep = sum([c.sleep_hours for c in recent_checkins if c.sleep_hours]) / len([c for c in recent_checkins if c.sleep_hours]) if recent_checkins else 0
    
    med_compliance = sum([1 for c in recent_checkins if c.medication_compliance]) / len(recent_checkins) if recent_checkins else 0
    
    # Extract alerts
    health_alerts = []
    if avg_mood < 4:
        health_alerts.append("⚠️ Low mood detected - consider reaching out to mental health resources")
    if avg_energy < 3:
        health_alerts.append("⚠️ Low energy levels - ensure adequate rest and nutrition")
    
    metrics = HealthMetricsSummary(
        average_mood=round(avg_mood, 1),
        average_energy=round(avg_energy, 1),
        average_sleep=round(avg_sleep, 1),
        mood_trend="stable",
        recent_symptoms=[c.symptoms for c in recent_checkins if c.symptoms][:3],
        medication_compliance_rate=round(med_compliance * 100, 1),
        entries_this_week=len(recent_checkins)
    )
    
    return HealthDashboard(
        user=user,
        metrics=metrics,
        recent_checkings=recent_checkins,
        recent_mood_entries=recent_moods,
        active_medications=active_meds,
        health_alerts=health_alerts
    )


# ==================== Root Endpoint ====================
@app.get("/")
def root():
    """Welcome to Toothless AI Health Assistant"""
    return {
        "message": "🐉 Welcome to Toothless - Your AI Health Assistant",
        "version": settings.APP_VERSION,
        "description": "Your personal AI health companion for daily check-ins, mood tracking, and health insights",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "users": "/users",
            "health_checkins": "/health-checkins",
            "mood_entries": "/mood-entries",
            "medications": "/medications",
            "toothless_chat": "/toothless/chat",
            "dashboard": "/dashboard/{user_id}"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
