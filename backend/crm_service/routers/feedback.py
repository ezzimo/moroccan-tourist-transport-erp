"""
Feedback management routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session
from services.feedback_service import FeedbackService
from schemas.feedback import (
    FeedbackCreate, FeedbackUpdate, FeedbackResponse, FeedbackStats
)
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import uuid


router = APIRouter(prefix="/feedback", tags=["Feedback Management"])


@router.post("/", response_model=FeedbackResponse)
async def create_feedback(
    feedback_data: FeedbackCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "create", "feedback"))
):
    """Submit new feedback"""
    feedback_service = FeedbackService(session)
    return await feedback_service.create_feedback(feedback_data)


@router.get("/", response_model=PaginatedResponse[FeedbackResponse])
async def get_feedback_list(
    pagination: PaginationParams = Depends(),
    customer_id: Optional[uuid.UUID] = Query(None, description="Filter by customer ID"),
    service_type: Optional[str] = Query(None, description="Filter by service type"),
    rating: Optional[int] = Query(None, ge=1, le=5, description="Filter by rating"),
    resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
    booking_id: Optional[uuid.UUID] = Query(None, description="Filter by booking ID"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "read", "feedback"))
):
    """Get list of feedback with optional filters"""
    feedback_service = FeedbackService(session)
    
    feedback_list, total = await feedback_service.get_feedback_list(
        pagination=pagination,
        customer_id=customer_id,
        service_type=service_type,
        rating=rating,
        resolved=resolved,
        booking_id=booking_id
    )
    
    return PaginatedResponse.create(
        items=feedback_list,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/stats", response_model=FeedbackStats)
async def get_feedback_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days for statistics"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "read", "feedback"))
):
    """Get feedback statistics"""
    feedback_service = FeedbackService(session)
    return await feedback_service.get_feedback_stats(days)


@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "read", "feedback"))
):
    """Get feedback by ID"""
    feedback_service = FeedbackService(session)
    return await feedback_service.get_feedback(feedback_id)


@router.put("/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
    feedback_id: uuid.UUID,
    feedback_data: FeedbackUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "update", "feedback"))
):
    """Update feedback (mainly for resolution)"""
    # Set resolved_by to current user if marking as resolved
    if feedback_data.resolved and not feedback_data.resolved_by:
        feedback_data.resolved_by = current_user.user_id
    
    feedback_service = FeedbackService(session)
    return await feedback_service.update_feedback(feedback_id, feedback_data)


@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "delete", "feedback"))
):
    """Delete feedback"""
    feedback_service = FeedbackService(session)
    return await feedback_service.delete_feedback(feedback_id)


# Customer-specific feedback endpoints
@router.get("/customer/{customer_id}", response_model=PaginatedResponse[FeedbackResponse])
async def get_customer_feedback(
    customer_id: uuid.UUID,
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "read", "feedback"))
):
    """Get all feedback for a specific customer"""
    feedback_service = FeedbackService(session)
    
    feedback_list, total = await feedback_service.get_customer_feedback(
        customer_id=customer_id,
        pagination=pagination
    )
    
    return PaginatedResponse.create(
        items=feedback_list,
        total=total,
        page=pagination.page,
        size=pagination.size
    )