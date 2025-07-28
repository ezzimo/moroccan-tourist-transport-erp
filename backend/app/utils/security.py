"""
Security utilities for password hashing and token management
"""
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import secrets
import string

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def generate_random_password(length: int = 12) -> str:
    """Generate a secure random password"""
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special_chars = "!@#$%^&*"
    
    # Ensure at least one character from each set
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special_chars)
    ]
    
    # Fill the rest with random characters from all sets
    all_chars = lowercase + uppercase + digits + special_chars
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))
    
    # Shuffle the password list
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


def is_password_strong(password: str) -> tuple[bool, list[str]]:
    """Check if password meets strength requirements"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character")
    
    return len(errors) == 0, errors




# JWT Token management (placeholder implementations)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token - placeholder for existing implementation"""
    # This should be implemented with actual JWT logic
    # For now, return a placeholder to avoid import errors
    return "placeholder_token"


def verify_token(token: str) -> dict:
    """Verify JWT token - placeholder for existing implementation"""
    # This should be implemented with actual JWT verification logic
    # For now, return a placeholder to avoid import errors
    return {"sub": "placeholder"}


def blacklist_token(token: str) -> bool:
    """Blacklist a token - placeholder for existing implementation"""
    # This should be implemented with actual blacklist logic
    # For now, return True to avoid import errors
    return True


def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted - placeholder for existing implementation"""
    # This should be implemented with actual blacklist check logic
    # For now, return False to avoid import errors
    return False

