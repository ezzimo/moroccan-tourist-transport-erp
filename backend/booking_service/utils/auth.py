"""
Authentication utilities for booking service
"""
from fastapi import Depends, HTTPException, status, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from config import settings
from typing import Optional, Dict, Any, List
import httpx
import uuid
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()


class CurrentUser:
    """Current user information from auth service"""
    def __init__(self, user_id: uuid.UUID, email: str, full_name: str, permissions: List[str]):
        self.user_id = user_id
        self.email = email
        self.full_name = full_name
        self.permissions = permissions
    
    def has_permission(self, service_name: str, action: str, resource: str = "*") -> bool:
        """Check if user has specific permission"""
        permission_variants = [
            f"{service_name}:{action}:{resource}",       # Exact match
            f"{service_name}:{action}:all",               # Allow if resource is 'all'
            f"{service_name}:{action}:*",                 # Wildcard resource
            f"{service_name}:*:{resource}",               # Wildcard action
            f"{service_name}:*:*",                        # Full service access
            f"*:*:*"                                      # Super admin
        ]
        
        return any(p in self.permissions for p in permission_variants)


async def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token locally with audience validation"""
    try:
        # Determine audience validation
        verify_aud = not settings.jwt_disable_audience_check
        options = {"verify_aud": verify_aud}
        
        # Get expected audiences
        expected_audiences = settings.jwt_allowed_audiences
        audience = expected_audiences[0] if expected_audiences else settings.jwt_audience
        
        logger.debug(f"Verifying JWT with audience={audience}, verify_aud={verify_aud}")
        
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            audience=audience if verify_aud else None,
            issuer=settings.jwt_issuer if verify_aud else None,
            options=options
        )
        
        # Additional audience check if multiple audiences allowed
        if verify_aud and len(expected_audiences) > 1:
            token_aud = payload.get('aud')
            if token_aud not in expected_audiences:
                logger.warning(f"Token audience '{token_aud}' not in allowed audiences {expected_audiences}")
                return None
        
        logger.debug(f"Local JWT verification successful for user: {payload.get('email', 'unknown')}")
        return payload
        
    except JWTError as e:
        logger.debug(f"Local JWT verification failed: {e}")
        return None


async def verify_auth_token_remote(token: str) -> Optional[Dict[str, Any]]:
    """Verify token with auth service as fallback"""
    try:
        logger.debug(f"Calling auth service at: {settings.auth_service_url}/api/v1/auth/me")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.auth_service_url}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            
            logger.debug(f"Auth service response status: {response.status_code}")
            
            if response.status_code == 200:
                user_data = response.json()
                logger.debug(f"Auth service returned user: {user_data.get('email', 'unknown')}")
                return user_data
            else:
                logger.warning(f"Auth service error: {response.status_code} - {response.text}")
                
    except Exception as e:
        logger.error(f"Error calling auth service: {e}")
    
    return None


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> CurrentUser:
    """Get current authenticated user with principal population"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials or not credentials.credentials:
        raise credentials_exception
    
    token = credentials.credentials
    user_data = None
    
    # Try local JWT verification first
    jwt_payload = await verify_jwt_token(token)
    if jwt_payload:
        # For local JWT, we need to get full user data from auth service
        user_data = await verify_auth_token_remote(token)
    else:
        # If local verification fails, try remote verification
        user_data = await verify_auth_token_remote(token)
    
    if not user_data:
        raise credentials_exception
    
    try:
        # Extract user information and populate principal
        current_user = CurrentUser(
            user_id=uuid.UUID(user_data["id"]),
            email=user_data["email"],
            full_name=user_data.get("full_name", ""),
            permissions=user_data.get("permissions", [])
        )
        
        # Populate request state for downstream use
        request.state.user = current_user
        
        logger.debug(f"Principal populated for user: {current_user.email}")
        return current_user
        
    except (KeyError, ValueError) as e:
        logger.error(f"Error extracting user data: {e}")
        logger.error(f"User data received: {user_data}")
        raise credentials_exception


def require_permission(service_name: str, action: str, resource: str = "*"):
    """Dependency to check if user has required permission"""
    def permission_checker(
        request: Request,
        current_user: CurrentUser = Depends(get_current_user)
    ) -> CurrentUser:
        required_permission = f"{service_name}:{action}:{resource}"
        
        if not current_user.has_permission(service_name, action, resource):
            # Enhanced logging before 403
            logger.warning(
                f"Permission denied - Required: {required_permission}, "
                f"User: {current_user.email} (ID: {current_user.user_id}), "
                f"User permissions: {current_user.permissions[:10]}..."  # Log first 10 permissions
            )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {required_permission}"
            )
        
        logger.debug(f"Permission granted: {required_permission} for user {current_user.email}")
        return current_user
    
    return permission_checker