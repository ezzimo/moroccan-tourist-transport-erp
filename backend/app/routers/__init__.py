"""
API routers for the authentication microservice
"""
from .auth import router as auth_router
from .users import router as users_router
from .roles import router as roles_router

__all__ = ["auth_router", "users_router", "roles_router"]