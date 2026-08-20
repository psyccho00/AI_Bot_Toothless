from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from models.user import User
from models.profile import HealthProfile, MedicalCondition, Allergy, WeightHistory
from models.medication import Medication
from schemas.user import (
    ProfileCreate,
    ProfileUpdateRequest,
    ProfileLoginRequest,
    RememberMeLoginRequest,
    ProfileDetailResponse,
    ProfileSelectionResponse
)
from auth.crypto import hash_pin
from sessions.manager import session_manager

router = APIRouter(prefix="/users/profiles", tags=["Profiles"])

@router.get("", response_model=List[ProfileSelectionResponse])
def get_profiles(db: Session = Depends(get_db)):
    """Retrieve all active profiles for selection"""
    users = db.query(User).filter(User.is_active == True).all()
    # Sort by last login (most recent first), fallback to creation date
    users.sort(key=lambda u: u.last_login or u.created_at or datetime.min, reverse=True)
    return users

@router.post("", status_code=status.HTTP_201_CREATED)
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    """Create a new user account profile and populate normalized health sub-tables"""
    # Check if profile name (username) already exists
    existing_user = db.query(User).filter(User.username == profile.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A profile with this name already exists."
        )
        
    # 1. Create primary User account with hashed PIN
    hashed_password = hash_pin(profile.password)
    new_user = User(
        username=profile.username,
        hashed_password=hashed_password
    )
    db.add(new_user)
    
    # 2. Create the associated Health Profile record explicitly
    new_profile = HealthProfile(
        user=new_user,
        full_name=profile.full_name,
        date_of_birth=datetime.combine(profile.date_of_birth, datetime.min.time()),
        gender=profile.gender,
        height=profile.height,
        weight=profile.weight,
        blood_group=profile.blood_group,
        avatar=profile.avatar,
        emergency_contact_name=profile.emergency_contact_name,
        emergency_contact_relationship=profile.emergency_contact_relationship,
        emergency_contact_phone=profile.emergency_contact_phone,
        occupation=profile.occupation,
        smoking_status=profile.smoking_status,
        alcohol_consumption=profile.alcohol_consumption,
        exercise_frequency=profile.exercise_frequency,
        preferred_language=profile.preferred_language
    )
    new_user.health_profile = new_profile
    db.add(new_profile)
    
    # Add initial weight history record
    new_profile.weight_histories.append(WeightHistory(weight=profile.weight))
    
    # 4. Populate initial allergies
    if profile.allergies:
        names = [a.strip() for a in profile.allergies.split(",") if a.strip()]
        categories = []
        if profile.allergies_categories:
            categories = [c.strip() for c in profile.allergies_categories.split(",") if c.strip()]
            
        for i, name in enumerate(names):
            category = categories[i] if i < len(categories) else "Other"
            new_profile.allergies.append(Allergy(
                allergy_name=name,
                category=category
            ))
            
    # 5. Populate initial medical conditions
    if profile.existing_conditions:
        for name in [c.strip() for c in profile.existing_conditions.split(",") if c.strip()]:
            new_profile.conditions.append(MedicalCondition(
                condition_name=name,
                is_resolved=False
            ))
            
    # 6. Populate initial medications
    if profile.current_medications:
        for name in [m.strip() for m in profile.current_medications.split(",") if m.strip()]:
            new_user.medications.append(Medication(
                name=name,
                dosage="As prescribed",
                frequency="As prescribed",
                is_active=True
            ))
            
    db.commit()
    db.refresh(new_user)
    return {"message": "Profile created successfully", "profile_id": new_user.id}

@router.post("/remember-me/login")
def remember_me_login(request_data: RememberMeLoginRequest, db: Session = Depends(get_db)):
    """Authenticate profile session using persistent remember-me tokens"""
    success = session_manager.verify_remember_me(db, request_data.user_id, request_data.token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired remember-me token."
        )
        
    return {"message": "Persistent login successful", "user_id": request_data.user_id}

@router.post("/{profile_id}/login")
def login_profile(profile_id: str, request_data: ProfileLoginRequest, db: Session = Depends(get_db)):
    """Authenticate profile session using PIN/Password"""
    success = session_manager.authenticate_profile(db, profile_id, request_data.pin)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid profile PIN or password."
        )
        
    return {"message": "Authentication successful", "user_id": profile_id}

@router.post("/{profile_id}/remember-me/register")
def register_remember_me(profile_id: str, db: Session = Depends(get_db)):
    """Generate and return a new remember-me token for a logged-in profile"""
    try:
        raw_token = session_manager.create_remember_me_token(db, profile_id)
        return {"token": raw_token}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{profile_id}/logout")
def logout_profile(profile_id: str, db: Session = Depends(get_db)):
    """Revoke remember-me authentication token and log profile out"""
    session_manager.revoke_remember_me(db, profile_id)
    return {"message": "Logout successful"}

@router.get("/{profile_id}", response_model=ProfileDetailResponse)
def get_profile_details(profile_id: str, db: Session = Depends(get_db)):
    """Fetch all detailed metadata for a specific health profile"""
    user = db.query(User).filter(User.id == profile_id, User.is_active == True).first()
    if not user or not user.health_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found."
        )
        
    hp = user.health_profile
    
    # Map sub-tables to string formats for backward compatible representation
    conditions = [c.condition_name for c in hp.conditions if not c.is_resolved]
    allergies = [a.allergy_name for a in hp.allergies]
    medications = [m.name for m in user.medications if m.is_active]
    
    return {
        "id": user.id,
        "username": user.username,
        "full_name": hp.full_name,
        "date_of_birth": hp.date_of_birth.date(),
        "age": user.age,
        "gender": hp.gender,
        "height": hp.height,
        "weight": hp.weight,
        "blood_group": hp.blood_group,
        "avatar": hp.avatar,
        "last_login": user.last_login,
        "emergency_contact_name": hp.emergency_contact_name,
        "emergency_contact_relationship": hp.emergency_contact_relationship,
        "emergency_contact_phone": hp.emergency_contact_phone,
        "occupation": hp.occupation,
        "smoking_status": hp.smoking_status,
        "alcohol_consumption": hp.alcohol_consumption,
        "exercise_frequency": hp.exercise_frequency,
        "preferred_language": hp.preferred_language,
        "conditions": ", ".join(conditions) if conditions else "None reported",
        "allergies": ", ".join(allergies) if allergies else "None reported",
        "medications": ", ".join(medications) if medications else "None reported",
        "weight_history": hp.weight_histories
    }

@router.put("/{profile_id}")
def update_profile(profile_id: str, update_data: ProfileUpdateRequest, db: Session = Depends(get_db)):
    """Update profile metrics and synchronize related normalized tables"""
    user = db.query(User).filter(User.id == profile_id, User.is_active == True).first()
    if not user or not user.health_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found."
        )
        
    hp = user.health_profile
    
    # 1. Log weight history if weight changed
    if hp.weight != update_data.weight:
        weight_log = WeightHistory(
            health_profile_id=hp.id,
            weight=update_data.weight
        )
        db.add(weight_log)
        
    # 2. Update basic demographics and lifestyle parameters
    hp.weight = update_data.weight
    hp.height = update_data.height
    hp.emergency_contact_name = update_data.emergency_contact_name
    hp.emergency_contact_relationship = update_data.emergency_contact_relationship
    hp.emergency_contact_phone = update_data.emergency_contact_phone
    
    hp.occupation = update_data.occupation
    hp.smoking_status = update_data.smoking_status
    hp.alcohol_consumption = update_data.alcohol_consumption
    hp.exercise_frequency = update_data.exercise_frequency
    hp.preferred_language = update_data.preferred_language
    
    hp.updated_at = datetime.utcnow()
    
    # 3. Synchronize medications (overwrite active list)
    # Mark old medications inactive or delete
    db.query(Medication).filter(Medication.user_id == user.id).delete()
    if update_data.medications and update_data.medications != "None reported":
        for name in [m.strip() for m in update_data.medications.split(",") if m.strip()]:
            med = Medication(
                user_id=user.id,
                name=name,
                dosage="As prescribed",
                frequency="As prescribed",
                is_active=True
            )
            db.add(med)
            
    # 4. Synchronize medical conditions (overwrite active list)
    db.query(MedicalCondition).filter(MedicalCondition.health_profile_id == hp.id).delete()
    if update_data.conditions and update_data.conditions != "None reported":
        for name in [c.strip() for c in update_data.conditions.split(",") if c.strip()]:
            cond = MedicalCondition(
                health_profile_id=hp.id,
                condition_name=name,
                is_resolved=False
            )
            db.add(cond)
            
    # 5. Synchronize allergies (overwrite active list)
    db.query(Allergy).filter(Allergy.health_profile_id == hp.id).delete()
    if update_data.allergies and update_data.allergies != "None reported":
        names = [a.strip() for a in update_data.allergies.split(",") if a.strip()]
        categories = []
        if update_data.allergies_categories:
            categories = [c.strip() for c in update_data.allergies_categories.split(",") if c.strip()]
            
        for i, name in enumerate(names):
            category = categories[i] if i < len(categories) else "Other"
            allergy = Allergy(
                health_profile_id=hp.id,
                allergy_name=name,
                category=category
            )
            db.add(allergy)
            
    db.commit()
    return {"message": "Profile updated successfully"}

@router.delete("/{profile_id}")
def delete_profile(profile_id: str, db: Session = Depends(get_db)):
    """Safely delete a profile and all its associated health records"""
    user = db.query(User).filter(User.id == profile_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found."
        )

    # 1. Revoke session / remember-me tokens
    session_manager.revoke_remember_me(db, profile_id)

    # 2. Delete user's related health records
    from models import HealthCheckIn, MoodEntry, Conversation
    db.query(HealthCheckIn).filter(HealthCheckIn.user_id == profile_id).delete()
    db.query(MoodEntry).filter(MoodEntry.user_id == profile_id).delete()
    db.query(Conversation).filter(Conversation.user_id == profile_id).delete()
    db.query(Medication).filter(Medication.user_id == profile_id).delete()

    # 3. Delete health profile sub-tables
    if user.health_profile:
        hp_id = user.health_profile.id
        db.query(WeightHistory).filter(WeightHistory.health_profile_id == hp_id).delete()
        db.query(MedicalCondition).filter(MedicalCondition.health_profile_id == hp_id).delete()
        db.query(Allergy).filter(Allergy.health_profile_id == hp_id).delete()
        db.query(HealthProfile).filter(HealthProfile.id == hp_id).delete()

    # 4. Delete user account record
    db.query(User).filter(User.id == profile_id).delete()
    db.commit()
    return {"message": "Profile deleted successfully"}

