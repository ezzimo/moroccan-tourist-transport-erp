"""
Security utilities for password hashing and JWT handling
"""
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from config import settings
from schemas.auth import TokenData
from typing import Optional
import uuid


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        exp: int = payload.get("exp")
        
        if user_id is None or email is None:
            return None
            
        return TokenData(
            user_id=uuid.UUID(user_id),
            email=email,
            exp=exp
        )
    except JWTError:
        return None


def is_token_blacklisted(token: str, redis_client) -> bool:
    """Check if token is blacklisted"""
    return redis_client.get(f"blacklist:{token}") is not None


def blacklist_token(token: str, redis_client, ttl: int = None):
    """Add token to blacklist"""
    if ttl is None:
        ttl = settings.access_token_expire_minutes * 60
    redis_client.setex(f"blacklist:{token}", ttl, "true")