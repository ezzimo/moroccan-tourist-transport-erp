"""
FastAPI dependencies for authentication and authorization
"""
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from database import get_session, get_redis
from models.user import User
from utils.security import verify_token, is_token_blacklisted
from schemas.auth import TokenData
from typing import Callable
import redis


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    
    # Check if token is blacklisted
    if is_token_blacklisted(token, redis_client):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token
    token_data: TokenData = verify_token(token)
    if token_data is None:
        raise credentials_exception
    
    # Get user from database
    statement = select(User).where(User.id == token_data.user_id)
    user = session.exec(statement).first()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_permission(service_name: str, action: str, resource: str = "*") -> Callable:
    """Dependency to check if user has required permission"""
    def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if not current_user.has_permission(service_name, action, resource):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {service_name}:{action}:{resource}"
            )
        return current_user
    
    return permission_checker