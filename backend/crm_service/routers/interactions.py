"""
Interaction management routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session
from services.interaction_service import InteractionService
from schemas.interaction import (
    InteractionCreate, InteractionUpdate, InteractionResponse, InteractionStats
)
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import uuid


router = APIRouter(prefix="/interactions", tags=["Interaction Management"])


@router.post("/", response_model=InteractionResponse)
async def create_interaction(
    interaction_data: InteractionCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "create", "interactions"))
):
    """Create a new interaction"""
    # Set staff member ID from current user if not provided
    if not interaction_data.staff_member_id:
        interaction_data.staff_member_id = current_user.user_id
    
    interaction_service = InteractionService(session)
    return await interaction_service.create_interaction(interaction_data)


@router.get("/", response_model=PaginatedResponse[InteractionResponse])
async def get_interactions(
    pagination: PaginationParams = Depends(),
    customer_id: Optional[uuid.UUID] = Query(None, description="Filter by customer ID"),
    staff_member_id: Optional[uuid.UUID] = Query(None, description="Filter by staff member ID"),
    channel: Optional[str] = Query(None, description="Filter by communication channel"),
    follow_up_required: Optional[bool] = Query(None, description="Filter by follow-up requirement"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "read", "interactions"))
):
    """Get list of interactions with optional filters"""
    interaction_service = InteractionService(session)
    
    interactions, total = await interaction_service.get_interactions(
        pagination=pagination,
        customer_id=customer_id,
        staff_member_id=staff_member_id,
        channel=channel,
        follow_up_required=follow_up_required
    )
    
    return PaginatedResponse.create(
        items=interactions,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/stats", response_model=InteractionStats)
async def get_interaction_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days for statistics"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "read", "interactions"))
):
    """Get interaction statistics"""
    interaction_service = InteractionService(session)
    return await interaction_service.get_interaction_stats(days)


@router.get("/{interaction_id}", response_model=InteractionResponse)
async def get_interaction(
    interaction_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "read", "interactions"))
):
    """Get interaction by ID"""
    interaction_service = InteractionService(session)
    return await interaction_service.get_interaction(interaction_id)


@router.put("/{interaction_id}", response_model=InteractionResponse)
async def update_interaction(
    interaction_id: uuid.UUID,
    interaction_data: InteractionUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "update", "interactions"))
):
    """Update interaction information"""
    interaction_service = InteractionService(session)
    return await interaction_service.update_interaction(interaction_id, interaction_data)


@router.delete("/{interaction_id}")
async def delete_interaction(
    interaction_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "delete", "interactions"))
):
    """Delete interaction"""
    interaction_service = InteractionService(session)
    return await interaction_service.delete_interaction(interaction_id)


# Customer-specific interaction endpoints
@router.get("/customer/{customer_id}", response_model=PaginatedResponse[InteractionResponse])
async def get_customer_interactions(
    customer_id: uuid.UUID,
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "read", "interactions"))
):
    """Get all interactions for a specific customer"""
    interaction_service = InteractionService(session)
    
    interactions, total = await interaction_service.get_customer_interactions(
        customer_id=customer_id,
        pagination=pagination
    )
    
    return PaginatedResponse.create(
        items=interactions,
        total=total,
        page=pagination.page,
        size=pagination.size
    )