"""
User preference management routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session
from services.preference_service import PreferenceService
from schemas.user_preference import (
    UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse,
    BulkPreferenceUpdate
)
from utils.auth import require_permission, CurrentUser
from typing import List, Optional
import uuid


router = APIRouter(prefix="/preferences", tags=["User Preferences"])


@router.post("/", response_model=UserPreferenceResponse)
async def create_user_preferences(
    preference_data: UserPreferenceCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("notification", "create", "preferences"))
):
    """Create user notification preferences"""
    preference_service = PreferenceService(session)
    return await preference_service.create_preference(preference_data)


@router.get("/", response_model=List[UserPreferenceResponse])
async def get_all_preferences(
    user_type: Optional[str] = Query(None, description="Filter by user type"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("notification", "read", "preferences"))
):
    """Get all user preferences"""
    preference_service = PreferenceService(session)
    return await preference_service.get_all_preferences(user_type)


@router.get("/{user_id}", response_model=UserPreferenceResponse)
async def get_user_preferences(
    user_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("notification", "read", "preferences"))
):
    """Get user preferences by user ID"""
    preference_service = PreferenceService(session)
    return await preference_service.get_preference(user_id)


@router.put("/{user_id}", response_model=UserPreferenceResponse)
async def update_user_preferences(
    user_id: uuid.UUID,
    preference_data: UserPreferenceUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("notification", "update", "preferences"))
):
    """Update user notification preferences"""
    preference_service = PreferenceService(session)
    return await preference_service.update_preference(user_id, preference_data)


@router.delete("/{user_id}")
async def delete_user_preferences(
    user_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("notification", "delete", "preferences"))
):
    """Delete user preferences"""
    preference_service = PreferenceService(session)
    return await preference_service.delete_preference(user_id)


@router.post("/bulk-update")
async def bulk_update_preferences(
    bulk_update: BulkPreferenceUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("notification", "update", "preferences"))
):
    """Bulk update preferences for multiple users"""
    preference_service = PreferenceService(session)
    return await preference_service.bulk_update_preferences(bulk_update)


@router.get("/channel/{channel}", response_model=List[UserPreferenceResponse])
async def get_users_by_channel_preference(
    channel: str,
    notification_type: Optional[str] = Query(None, description="Filter by notification type"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("notification", "read", "preferences"))
):
    """Get users who have enabled a specific channel"""
    preference_service = PreferenceService(session)
    return await preference_service.get_users_by_channel_preference(channel, notification_type)


@router.put("/{user_id}/contact", response_model=UserPreferenceResponse)
async def update_contact_info(
    user_id: uuid.UUID,
    email: Optional[str] = Query(None, description="Email address"),
    phone: Optional[str] = Query(None, description="Phone number"),
    push_token: Optional[str] = Query(None, description="Push notification token"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("notification", "update", "preferences"))
):
    """Update user contact information"""
    preference_service = PreferenceService(session)
    return await preference_service.update_contact_info(user_id, email, phone, push_token)