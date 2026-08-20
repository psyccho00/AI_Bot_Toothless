from datetime import datetime
from sqlalchemy.orm import Session
from models.user import User
from auth.crypto import (
    verify_pin,
    generate_remember_token,
    hash_remember_token,
    verify_remember_token
)

class SessionManager:
    """Manages profile sessions, PIN verification, and secure remember-me token exchanges"""
    
    def authenticate_profile(self, db: Session, user_id: str, pin: str) -> bool:
        """Verify the PIN for a specific profile and update last_login on success"""
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not user:
            return False
            
        if verify_pin(pin, user.hashed_password):
            user.last_login = datetime.utcnow()
            db.commit()
            return True
            
        return False

    def create_remember_me_token(self, db: Session, user_id: str) -> str:
        """Generate a secure remember-me token, save its hash to the database, and return the raw token"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("Profile not found")
            
        raw_token = generate_remember_token()
        user.remember_token = hash_remember_token(raw_token)
        db.commit()
        return raw_token

    def verify_remember_me(self, db: Session, user_id: str, raw_token: str) -> bool:
        """Authenticate a user using a raw remember-me token matches the hashed token in database"""
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not user or not user.remember_token:
            return False
            
        if verify_remember_token(raw_token, user.remember_token):
            user.last_login = datetime.utcnow()
            db.commit()
            return True
            
        return False

    def revoke_remember_me(self, db: Session, user_id: str) -> bool:
        """Clear the remember-me token for a profile (e.g. on logout)"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
            
        user.remember_token = None
        db.commit()
        return True

# Singleton session manager instance
session_manager = SessionManager()
