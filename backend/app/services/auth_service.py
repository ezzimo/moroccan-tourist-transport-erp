"""
Authentication service for login/logout operations
"""
from sqlmodel import Session, select
from fastapi import HTTPException, status
from models.user import User
from schemas.auth import LoginRequest, LoginResponse, TokenData
from schemas.user import UserResponse
from utils.security import verify_password, create_access_token, blacklist_token
from config import settings
from datetime import datetime, timedelta
import redis
import uuid


class AuthService:
    """Service for handling authentication operations"""
    
    def __init__(self, session: Session, redis_client: redis.Redis):
        self.session = session
        self.redis = redis_client
    
    async def login(self, login_data: LoginRequest) -> LoginResponse:
        """Authenticate user and return JWT token"""
        # Get user by email
        statement = select(User).where(User.email == login_data.email)
        user = self.session.exec(statement).first()
        
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is disabled"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "full_name": user.full_name
        }
        access_token = create_access_token(
            data=token_data, 
            expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse.model_validate(user)
        )
    
    async def logout(self, token: str) -> dict:
        """Logout user by blacklisting token"""
        # Add token to blacklist
        blacklist_token(token, self.redis)
        
        return {"message": "Successfully logged out"}
    
    async def verify_token(self, token: str) -> User:
        """Verify token and return user"""
        from utils.security import verify_token, is_token_blacklisted
        
        if is_token_blacklisted(token, self.redis):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
        
        token_data = verify_token(token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        statement = select(User).where(User.id == token_data.user_id)
        user = self.session.exec(statement).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user