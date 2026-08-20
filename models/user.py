import uuid
from datetime import datetime
from typing import Optional, Any, Dict
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from .base import Base
from utils.date_utils import calculate_age

class User(Base):
    """User model representing a distinct profile account with backward compatibility properties"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)  # PIN or password (hashed using bcrypt)
    remember_token = Column(String, nullable=True)  # SHA256 hashed Remember-Me token
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    health_profile = relationship("HealthProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    health_checkings = relationship("HealthCheckIn", back_populates="user", cascade="all, delete-orphan")
    mood_entries = relationship("MoodEntry", back_populates="user", cascade="all, delete-orphan")
    medications = relationship("Medication", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        # Extract profile-related parameters for backward compatibility on insertion
        hp_kwargs = {}
        for field in ['full_name', 'age', 'gender', 'date_of_birth']:
            if field in kwargs:
                hp_kwargs[field] = kwargs.pop(field)
                
        # Existing text columns for compatibility (extract and drop)
        medical_history = kwargs.pop('medical_history', None)
        allergies = kwargs.pop('allergies', None)
        current_medications = kwargs.pop('current_medications', None)
        
        # Populate basic User fields
        super().__init__(**kwargs)
        
        # Map values to a new HealthProfile
        # Set defaults if not provided in kwargs
        from .profile import HealthProfile, MedicalCondition, Allergy, WeightHistory
        from .medication import Medication
        
        # Only initialize HealthProfile if profile parameters are provided
        if hp_kwargs or medical_history or allergies or current_medications:
            dob = hp_kwargs.get('date_of_birth')
            if not dob:
                age_val = hp_kwargs.get('age', 30)
                today = datetime.utcnow()
                dob = datetime(today.year - int(age_val), today.month, today.day)
                
            self.health_profile = HealthProfile(
                full_name=hp_kwargs.get('full_name', self.username or "User"),
                date_of_birth=dob,
                gender=hp_kwargs.get('gender', "Unknown"),
                height=170.0,
                weight=70.0
            )
            self.health_profile.weight_histories.append(WeightHistory(weight=70.0))
            
            # Parse medical history, allergies, medications strings if provided
            if medical_history and medical_history != "None reported":
                for item in [c.strip() for c in medical_history.split(",") if c.strip()]:
                    self.health_profile.conditions.append(MedicalCondition(condition_name=item))
                    
            if allergies and allergies != "None reported":
                for item in [a.strip() for a in allergies.split(",") if a.strip()]:
                    self.health_profile.allergies.append(Allergy(allergy_name=item))
                    
            if current_medications and current_medications != "None reported":
                for item in [m.strip() for m in current_medications.split(",") if m.strip()]:
                    self.medications.append(Medication(
                        name=item,
                        dosage="As prescribed",
                        frequency="As prescribed",
                        start_date=datetime.utcnow(),
                        reason="Unspecified"
                    ))

    # Properties to maintain absolute compatibility with existing route handlers
    @property
    def full_name(self) -> str:
        return self.health_profile.full_name if self.health_profile else ""
    
    @full_name.setter
    def full_name(self, value: str):
        if not self.health_profile:
            self._init_default_profile()
        self.health_profile.full_name = value

    @property
    def age(self) -> int:
        if not self.health_profile or not self.health_profile.date_of_birth:
            return 30
        return calculate_age(self.health_profile.date_of_birth)
        
    @age.setter
    def age(self, value: Any):
        if not self.health_profile:
            self._init_default_profile()
        today = datetime.utcnow()
        self.health_profile.date_of_birth = datetime(today.year - int(value), today.month, today.day)

    @property
    def gender(self) -> str:
        return self.health_profile.gender if self.health_profile else ""
        
    @gender.setter
    def gender(self, value: str):
        if not self.health_profile:
            self._init_default_profile()
        self.health_profile.gender = value

    @property
    def medical_history(self) -> str:
        if not self.health_profile or not self.health_profile.conditions:
            return "None reported"
        active_conditions = [c.condition_name for c in self.health_profile.conditions if not c.is_resolved]
        return ", ".join(active_conditions) if active_conditions else "None reported"
        
    @medical_history.setter
    def medical_history(self, value: Optional[str]):
        if not self.health_profile:
            self._init_default_profile()
        self.health_profile.conditions = []
        if value and value != "None reported":
            from .profile import MedicalCondition
            for item in [c.strip() for c in value.split(",") if c.strip()]:
                self.health_profile.conditions.append(MedicalCondition(condition_name=item))

    @property
    def allergies(self) -> str:
        if not self.health_profile or not self.health_profile.allergies:
            return "None reported"
        names = [a.allergy_name for a in self.health_profile.allergies]
        return ", ".join(names) if names else "None reported"
        
    @allergies.setter
    def allergies(self, value: Optional[str]):
        if not self.health_profile:
            self._init_default_profile()
        self.health_profile.allergies = []
        if value and value != "None reported":
            from .profile import Allergy
            for item in [a.strip() for a in value.split(",") if a.strip()]:
                self.health_profile.allergies.append(Allergy(allergy_name=item))

    @property
    def current_medications(self) -> str:
        active_meds = [m for m in self.medications if m.is_active]
        if not active_meds:
            return "None reported"
        return ", ".join([f"{m.name} ({m.dosage}, {m.frequency})" for m in active_meds])
        
    @current_medications.setter
    def current_medications(self, value: Optional[str]):
        self.medications = []
        if value and value != "None reported":
            from .medication import Medication
            for item in [m.strip() for m in value.split(",") if m.strip()]:
                self.medications.append(Medication(
                    name=item,
                    dosage="As prescribed",
                    frequency="As prescribed",
                    start_date=datetime.utcnow(),
                    reason="Unspecified"
                ))

    def _init_default_profile(self):
        from .profile import HealthProfile, WeightHistory
        today = datetime.utcnow()
        self.health_profile = HealthProfile(
            full_name=self.username or "User",
            date_of_birth=datetime(today.year - 30, today.month, today.day),
            gender="Unknown",
            height=170.0,
            weight=70.0
        )
        self.health_profile.weight_histories.append(WeightHistory(weight=70.0))
