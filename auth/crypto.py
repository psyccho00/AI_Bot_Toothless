import secrets
import hashlib
import bcrypt

def hash_pin(pin: str) -> str:
    """Hash a 4-digit PIN or password securely using bcrypt directly"""
    pin_bytes = pin.encode('utf-8')
    # Generate a salt and hash the pin
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pin_bytes, salt)
    return hashed.decode('utf-8')

def verify_pin(pin: str, hashed_pin: str) -> bool:
    """Verify a PIN or password against its bcrypt hash"""
    if not hashed_pin:
        return False
    try:
        pin_bytes = pin.encode('utf-8')
        hashed_bytes = hashed_pin.encode('utf-8')
        return bcrypt.checkpw(pin_bytes, hashed_bytes)
    except Exception:
        # Fallback in case of raw comparison during legacy transitions
        return pin == hashed_pin

def generate_remember_token() -> str:
    """Generate a cryptographically secure 64-character token for device authentication"""
    return secrets.token_hex(32)

def hash_remember_token(token: str) -> str:
    """Hash a remember-me token using SHA256 before saving to the database"""
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

def verify_remember_token(token: str, hashed_token: str) -> bool:
    """Verify a remember-me token against its SHA256 hash"""
    if not hashed_token or not token:
        return False
    return hash_remember_token(token) == hashed_token
