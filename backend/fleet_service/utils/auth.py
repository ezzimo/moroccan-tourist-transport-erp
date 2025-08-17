"""
Authentication utilities for fleet service
"""
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from config import settings
from typing import Optional, Dict, Any
import httpx
import uuid


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
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        print(f"Local JWT verification successful: {payload.get('email', 'unknown')}")
        return payload
    except JWTError as e:
        print(f"Local JWT verification failed: {e}")
        # If local verification fails, check with auth service
        try:
            print(f"Calling auth service at: {settings.auth_service_url}/api/v1/auth/me")
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.auth_service_url}/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                print(f"Auth service response status: {response.status_code}")
                if response.status_code == 200:
                    user_data = response.json()
                    print(f"Auth service returned user: {user_data.get('email', 'unknown')}")
                    return user_data
                else:
                    print(f"Auth service error: {response.text}")
        except Exception as e:
            print(f"Error calling auth service: {e}")
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
        print(f"Missing field in user data: {e}")
        print(f"User data received: {user_data}")
    except ValueError as e:
        print(f"Invalid UUID format: {e}")
        print(f"User data received: {user_data}")
    except Exception as e:
        print(f"Unexpected error in authentication: {e}")
        print(f"User data received: {user_data}")
    
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