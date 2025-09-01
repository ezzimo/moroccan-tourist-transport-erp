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
            f"{service_name}:{action}:{resource}",
            f"{service_name}:{action}:*",
            f"{service_name}:*:{resource}",
            f"{service_name}:*:*",
            "*:*:*"
        ]
        return any(perm in self.permissions for perm in permission_variants)


async def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token locally with audience validation"""
    try:
        # Decode with audience verification
        if not settings.jwt_disable_audience_check:
            # Check against allowed audiences
            for audience in settings.jwt_allowed_audiences:
                try:
                    payload = jwt.decode(
                        token,
                        settings.jwt_secret_key,
                        algorithms=[settings.jwt_algorithm],
                        audience=audience,
                        issuer=settings.jwt_issuer,
                        options={"verify_aud": True, "verify_iss": True}
                    )
                    logger.debug(f"JWT verified with audience: {audience}")
                    return payload
                except JWTError:
                    continue
            logger.warning("JWT failed audience verification for all allowed audiences")
            return None
        else:
            # Audience check disabled (development only)
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
                options={"verify_aud": False, "verify_iss": False}
            )
            logger.debug("JWT verified with audience check disabled")
            return payload
    except JWTError as e:
        logger.debug(f"JWT verification failed: {e}")
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
    
    token = credentials.credentials
    
    # Try local JWT verification first
    user_data = await verify_jwt_token(token)
    
    if not user_data:
        # Fallback to remote auth service verification
        user_data = await verify_auth_token_remote(token)
        
        if not user_data:
            logger.warning("Both local and remote token verification failed")
            raise credentials_exception
    
    # Extract user information and populate principal
    try:
        if "permissions" in user_data:
            # Response from auth service /me endpoint
            current_user = CurrentUser(
                user_id=uuid.UUID(user_data["id"]),
                email=user_data["email"],
                full_name=user_data.get("full_name", ""),
                permissions=user_data["permissions"]
            )
        else:
            # JWT payload - need to get permissions from auth service
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.auth_service_url}/api/v1/auth/permissions",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
                if response.status_code == 200:
                    permissions_data = response.json()
                    current_user = CurrentUser(
                        user_id=uuid.UUID(user_data["sub"]),
                        email=user_data["email"],
                        full_name=user_data.get("full_name", ""),
                        permissions=permissions_data["permissions"]
                    )
                else:
                    logger.error(f"Failed to get permissions from auth service: {response.status_code}")
                    raise credentials_exception
        
        # Store user in request state for downstream access
        request.state.user = current_user
        logger.debug(f"Principal populated for user: {current_user.email}")
        return current_user
        
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error extracting user data: {e}")
        logger.debug(f"User data received: {user_data}")
        raise credentials_exception


def require_permission(service_name: str, action: str, resource: str = "*"):
    """Dependency to check if user has required permission with enhanced logging"""
    def permission_checker(
        request: Request,
        current_user: CurrentUser = Depends(get_current_user)
    ) -> CurrentUser:
        required_permission = f"{service_name}:{action}:{resource}"
        
        if not current_user.has_permission(service_name, action, resource):
            # Enhanced debug logging before 403
            logger.debug(
                f"Permission denied - Required: {required_permission}, "
                f"User: {current_user.email} ({current_user.user_id}), "
                f"User permissions: {current_user.permissions[:10]}..."  # First 10 for brevity
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {required_permission}"
            )
        
        logger.debug(f"Permission granted: {required_permission} for user {current_user.email}")
        return current_user
    
    return permission_checker