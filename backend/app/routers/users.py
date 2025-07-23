"""
User management routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session
from services.user_service import UserService
from schemas.user import UserCreate, UserUpdate, UserResponse, UserWithRoles
from utils.dependencies import require_permission
from typing import List
import uuid


router = APIRouter(prefix="/users", tags=["User Management"])


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("auth", "create", "users"))
):
    """Create a new user"""
    user_service = UserService(session)
    return await user_service.create_user(user_data)


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("auth", "read", "users"))
):
    """Get list of users"""
    user_service = UserService(session)
    return await user_service.get_users(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserWithRoles)
async def get_user(
    user_id: uuid.UUID,
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("auth", "read", "users"))
):
    """Get user by ID"""
    user_service = UserService(session)
    return await user_service.get_user(user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdate,
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("auth", "update", "users"))
):
    """Update user information"""
    user_service = UserService(session)
    return await user_service.update_user(user_id, user_data)


@router.delete("/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("auth", "delete", "users"))
):
    """Delete user (soft delete)"""
    user_service = UserService(session)
    return await user_service.delete_user(user_id)