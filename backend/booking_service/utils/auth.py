"""
Authentication utilities for booking service
"""
from fastapi import Depends, HTTPException, status, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from jose.exceptions import JWTClaimsError
from ..config import settings
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
            "*:*:*",
        ]
        return any(p in self.permissions for p in permission_variants)


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify JWT token with audience validation (SYNC, NO AWAIT HERE).
    Returns payload dict when valid, otherwise None.
    """
    try:
        # Safeguard defaults in case settings doesn’t define them
        allowed_audiences: List[str] = getattr(settings, "jwt_allowed_audiences", []) or []
        disable_aud_check: bool = bool(getattr(settings, "jwt_disable_audience_check", False))
        jwt_secret_key: str = getattr(settings, "jwt_secret_key")
        jwt_algorithm: str = getattr(settings, "jwt_algorithm", "HS256")
        jwt_issuer: Optional[str] = getattr(settings, "jwt_issuer", None)

        if not jwt_secret_key:
            logger.error("JWT secret key is not configured")
            return None

        base_kwargs = {
            "key": jwt_secret_key,
            "algorithms": [jwt_algorithm],
        }
        # jose only verifies issuer if provided
        if jwt_issuer:
            base_kwargs["issuer"] = jwt_issuer

        if disable_aud_check or not allowed_audiences:
            # Decode WITHOUT audience verification
            payload = jwt.decode(token, options={"verify_aud": False}, **base_kwargs)
            logger.debug(f"JWT decoded without audience check for user: {payload.get('email', 'unknown')}")
            return payload

        # Try each allowed audience (emulate multi-aud)
        last_error: Optional[Exception] = None
        for audience in allowed_audiences:
            try:
                payload = jwt.decode(token, audience=audience, **base_kwargs)
                logger.debug(f"JWT verified with audience '{audience}' for user: {payload.get('email', 'unknown')}")
                return payload
            except (JWTClaimsError, JWTError) as e:
                last_error = e
                continue

        logger.warning(f"JWT local verification failed for all audiences {allowed_audiences}: {last_error}")
        return None

    except Exception as e:
        logger.error(f"JWT verification error: {e}")
        return None  # DO NOT await here; caller handles async fallback


async def _verify_with_auth_service(token: str) -> Optional[Dict[str, Any]]:
    """Fallback verification with remote auth service (ASYNC)"""
    try:
        auth_service_url: str = getattr(settings, "auth_service_url", "").rstrip("/")
        if not auth_service_url:
            logger.error("auth_service_url is not configured")
            return None

        logger.debug(f"Trying remote auth service: {auth_service_url}")
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{auth_service_url}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
        if response.status_code == 200:
            user_data = response.json()
            logger.debug(f"Remote auth verification successful: {user_data.get('email', 'unknown')}")
            return user_data

        logger.warning(f"Remote auth service returned {response.status_code}: {response.text[:200]}")
        return None

    except Exception as e:
        logger.error(f"Remote auth service error: {e}")
        return None


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security),
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

    # 1) Try local sync JWT verification
    user_data = verify_jwt_token(token)

    # 2) If local JWT failed, try remote verification (async)
    if not user_data:
        user_data = await _verify_with_auth_service(token)

    if not user_data:
        raise credentials_exception

    try:
        # Two shapes:
        # - /me response: has "permissions" and "id"
        # - raw JWT payload: no "permissions", has "sub"
        if "permissions" in user_data:
            current_user = CurrentUser(
                user_id=uuid.UUID(user_data["id"]),
                email=user_data["email"],
                full_name=user_data.get("full_name", ""),
                permissions=user_data["permissions"],
            )
        else:
            # Need to fetch permissions
            auth_service_url: str = getattr(settings, "auth_service_url", "").rstrip("/")
            if not auth_service_url:
                logger.error("auth_service_url is not configured for permissions fetch")
                raise credentials_exception

            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{auth_service_url}/api/v1/auth/permissions",
                    headers={"Authorization": f"Bearer {token}"},
                )
            if resp.status_code != 200:
                raise credentials_exception

            permissions_data = resp.json()
            current_user = CurrentUser(
                user_id=uuid.UUID(user_data["sub"]),
                email=user_data["email"],
                full_name=user_data.get("full_name", ""),
                permissions=permissions_data.get("permissions", []),
            )

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
        current_user: CurrentUser = Depends(get_current_user),
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
                detail=f"Permission denied: {required_permission}",
            )

        logger.debug(f"Permission granted: {required_permission} for user {current_user.email}")
        return current_user

    return permission_checker
