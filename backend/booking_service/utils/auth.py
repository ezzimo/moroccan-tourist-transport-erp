"""
Authentication utilities for booking service with enhanced error handling
"""
from fastapi import Depends, HTTPException, status, Security
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


async def verify_auth_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify token with enhanced error handling and fallback"""
    try:
        # First try local JWT verification for performance
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm],
                options={
                    "verify_aud": not settings.jwt_disable_audience_check,
                    "verify_iss": True
                },
                audience=settings.jwt_allowed_audiences if not settings.jwt_disable_audience_check else None,
                issuer=settings.jwt_issuer
            )
            logger.debug(f"Local JWT verification successful for user: {payload.get('email', 'unknown')}")
            return payload
        except JWTError as jwt_error:
            logger.debug(f"Local JWT verification failed: {jwt_error}")
            # Continue to auth service verification
        
        # Fallback to auth service verification
        logger.debug(f"Calling auth service at: {settings.auth_service_url}/api/v1/auth/me")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.auth_service_url}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            logger.debug(f"Auth service response status: {response.status_code}")
            
            if response.status_code == 200:
                user_data = response.json()
                logger.debug(f"Auth service returned user: {user_data.get('email', 'unknown')}")
                return user_data
            else:
                logger.warning(f"Auth service error: {response.status_code} - {response.text}")
                return None
                
    except httpx.TimeoutException:
        logger.error("Auth service timeout")
        return None
    except httpx.RequestError as e:
        logger.error(f"Auth service connection error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in token verification: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> CurrentUser:
    """Get current authenticated user with comprehensive error handling"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials or not credentials.credentials:
        logger.warning("No credentials provided")
        raise credentials_exception
    
    token = credentials.credentials
    user_data = await verify_auth_token(token)
    
    if not user_data:
        logger.warning("Token verification failed")
        raise credentials_exception
    
    try:
        # Handle both JWT payload and auth service response formats
        if "permissions" in user_data:
            # Response from auth service /me endpoint
            return CurrentUser(
                user_id=uuid.UUID(user_data["id"]),
                email=user_data["email"],
                full_name=user_data.get("full_name", ""),
                permissions=user_data["permissions"]
            )
        else:
            # JWT payload - need to get permissions from auth service
            logger.debug("Getting permissions from auth service")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{settings.auth_service_url}/api/v1/auth/permissions",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    permissions_data = response.json()
                    return CurrentUser(
                        user_id=uuid.UUID(user_data["sub"]),
                        email=user_data["email"],
                        full_name=user_data.get("full_name", ""),
                        permissions=permissions_data["permissions"]
                    )
                else:
                    logger.error(f"Failed to get permissions: {response.status_code}")
                    raise credentials_exception
                    
    except KeyError as e:
        logger.error(f"Missing field in user data: {e}")
        logger.error(f"User data received: {user_data}")
        raise credentials_exception
    except ValueError as e:
        logger.error(f"Invalid UUID format: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error in authentication: {e}")
        raise credentials_exception


def require_permission(service_name: str, action: str, resource: str = "*"):
    """Dependency to check if user has required permission"""
    def permission_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not current_user.has_permission(service_name, action, resource):
            logger.warning(
                f"Permission denied for user {current_user.email}: "
                f"required {service_name}:{action}:{resource}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {service_name}:{action}:{resource}"
            )
        return current_user
    
    return permission_checker