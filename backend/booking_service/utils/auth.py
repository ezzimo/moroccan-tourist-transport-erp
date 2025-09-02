"""
Authentication utilities for booking service
"""
from fastapi import Depends, HTTPException, status, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from jose.exceptions import JWTClaimsError
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
        return any(p in self.permissions for p in permission_variants)


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token with audience validation"""
    try:
        # Get allowed audiences
        allowed_audiences = settings.jwt_allowed_audiences
        
        if settings.jwt_disable_audience_check:
            # Decode without audience verification
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
                options={"verify_aud": False},
                issuer=settings.jwt_issuer
            )
            logger.debug(f"JWT decoded without audience check for user: {payload.get('email', 'unknown')}")
            return payload
        
        # Try each allowed audience
        last_error = None
        for audience in allowed_audiences:
            try:
                payload = jwt.decode(
                    token,
                    settings.jwt_secret_key,
                    algorithms=[settings.jwt_algorithm],
                    audience=audience,
                    issuer=settings.jwt_issuer
                )
                logger.debug(f"JWT verified with audience '{audience}' for user: {payload.get('email', 'unknown')}")
                return payload
            except JWTClaimsError as e:
                last_error = e
                continue
            except JWTError as e:
                last_error = e
                break
        
        # Log consolidated error once
        logger.warning(f"JWT local verification failed for all audiences {allowed_audiences}: {last_error}")
        
    except Exception as e:
        logger.error(f"JWT verification error: {e}")
        
    # Fallback to remote auth service verification
    return await _verify_with_auth_service(token)


async def _verify_with_auth_service(token: str) -> Optional[Dict[str, Any]]:
    """Fallback verification with remote auth service"""
    try:
        logger.debug(f"Trying remote auth service: {settings.auth_service_url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.auth_service_url}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
            if response.status_code == 200:
                user_data = response.json()
                logger.debug(f"Remote auth verification successful: {user_data.get('email', 'unknown')}")
                return user_data
            else:
                logger.warning(f"Remote auth service returned {response.status_code}: {response.text[:200]}")
    except Exception as e:
        logger.error(f"Remote auth service error: {e}")
    
    return None
async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> CurrentUser:
    """Get current authenticated user and populate request state"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials or not credentials.credentials:
        raise credentials_exception
    
    token = credentials.credentials
    user_data = verify_jwt_token(token)
    
    # If local JWT failed, try remote verification
    if not user_data:
        user_data = await _verify_with_auth_service(token)
    
    if not user_data:
        raise credentials_exception
    
    try:
        # Handle both JWT payload and auth service response formats
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
                    timeout=5.0
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
                    raise credentials_exception
        
        # Populate request state for downstream use
        request.state.user = current_user
        return current_user
        
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Error processing user data: {e}, data: {user_data}")
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
                f"User: {current_user.email} ({current_user.user_id}), "
                f"User permissions (first 10): {current_user.permissions[:10]}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {required_permission}"
            )
        
        logger.debug(f"Permission granted: {required_permission} for user {current_user.email}")
        return current_user
    
    return permission_checker