"""
Authentication utilities for CRM service
"""
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from config import settings
from typing import Optional, Dict, Any
import httpx
import uuid
import logging

logger = logging.getLogger(__name__)


security = HTTPBearer()


class CurrentUser:
    """Current user information from auth service"""
    def __init__(self, user_id: uuid.UUID, email: str, full_name: str, permissions: list):
        self.user_id = user_id
        self.email = email
        self.full_name = full_name
        self.permissions = permissions
    
    def has_permission(self, service_name: str, action: str, resource: str = "*") -> bool:
        """Check if user has specific permission"""
        permission_string = f"{service_name}:{action}:{resource}"
        wildcard_permission = f"{service_name}:{action}:*"
        return permission_string in self.permissions or wildcard_permission in self.permissions


async def verify_auth_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify token with auth service"""
    try:
        # First try local JWT verification for performance
        # Handle audience verification based on configuration
        decode_options = {"verify_aud": not settings.jwt_disable_audience_check}
        
        if settings.jwt_disable_audience_check:
            payload = jwt.decode(
                token, 
                settings.secret_key, 
                algorithms=[settings.algorithm],
                options=decode_options
            )
            logger.debug(f"JWT decoded without audience check for user: {payload.get('email', 'unknown')}")
            return payload
        else:
            # Try each allowed audience
            last_error = None
            for audience in settings.jwt_allowed_audiences:
                try:
                    payload = jwt.decode(
                        token,
                        settings.secret_key,
                        algorithms=[settings.algorithm],
                        audience=audience,
                        issuer=settings.jwt_issuer
                    )
                    logger.debug(f"JWT verified with audience '{audience}' for user: {payload.get('email', 'unknown')}")
                    break
                except jwt.JWTClaimsError as e:
                    last_error = e
                    continue
                except jwt.JWTError as e:
                    last_error = e
                    break
            else:
                # No audience worked, raise the last error
                if last_error:
                    logger.warning(f"JWT verification failed for all audiences {settings.jwt_allowed_audiences}: {last_error}")
                    raise last_error
        
        return payload
    except JWTError as e:
        logger.warning(f"Local JWT verification failed: {e}")
        # If local verification fails, check with auth service
        return await _verify_with_auth_service(token)
    except Exception as e:
        logger.error(f"Unexpected JWT verification error: {e}")
    return None


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
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> CurrentUser:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    user_data = await verify_auth_token(token)
    
    if not user_data:
        raise credentials_exception
    
    # Extract user information from token or auth service response
    try:
        if "permissions" in user_data:
            # Response from auth service
            return CurrentUser(
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
    except KeyError as e:
        logger.error(f"Missing field in user data: {e}, data keys: {list(user_data.keys()) if user_data else 'None'}")
    except ValueError as e:
        logger.error(f"Invalid UUID format: {e}, user_id: {user_data.get('id') or user_data.get('sub', 'missing')}")
    except Exception as e:
        logger.error(f"Unexpected error in authentication: {e}")
    
    raise credentials_exception


def require_permission(service_name: str, action: str, resource: str = "*"):
    """Dependency to check if user has required permission"""
    def permission_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not current_user.has_permission(service_name, action, resource):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {service_name}:{action}:{resource}"
            )
        return current_user
    
    return permission_checker