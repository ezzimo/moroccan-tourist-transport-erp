"""
Segment management routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session
from services.segment_service import SegmentService
from schemas.segment import (
    SegmentCreate, SegmentUpdate, SegmentResponse, SegmentWithCustomers
)
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import uuid


router = APIRouter(prefix="/segments", tags=["Segment Management"])


@router.post("/", response_model=SegmentResponse)
async def create_segment(
    segment_data: SegmentCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "create", "segments"))
):
    """Create a new customer segment"""
    segment_service = SegmentService(session)
    return await segment_service.create_segment(segment_data)


@router.get("/", response_model=PaginatedResponse[SegmentResponse])
async def get_segments(
    pagination: PaginationParams = Depends(),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "read", "segments"))
):
    """Get list of customer segments"""
    segment_service = SegmentService(session)
    
    segments, total = await segment_service.get_segments(
        pagination=pagination,
        is_active=is_active
    )
    
    return PaginatedResponse.create(
        items=segments,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/{segment_id}", response_model=SegmentResponse)
async def get_segment(
    segment_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "read", "segments"))
):
    """Get segment by ID"""
    segment_service = SegmentService(session)
    return await segment_service.get_segment(segment_id)


@router.get("/{segment_id}/customers", response_model=SegmentWithCustomers)
async def get_segment_customers(
    segment_id: uuid.UUID,
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "read", "segments"))
):
    """Get segment with its customers"""
    segment_service = SegmentService(session)
    return await segment_service.get_segment_customers(segment_id, pagination)


@router.put("/{segment_id}", response_model=SegmentResponse)
async def update_segment(
    segment_id: uuid.UUID,
    segment_data: SegmentUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "update", "segments"))
):
    """Update segment information"""
    segment_service = SegmentService(session)
    return await segment_service.update_segment(segment_id, segment_data)


@router.delete("/{segment_id}")
async def delete_segment(
    segment_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "delete", "segments"))
):
    """Delete segment"""
    segment_service = SegmentService(session)
    return await segment_service.delete_segment(segment_id)


@router.post("/customer/{customer_id}/assign")
async def assign_customer_segments(
    customer_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "update", "segments"))
):
    """Assign customer to matching segments"""
    segment_service = SegmentService(session)
    segments = await segment_service.assign_customer_to_segments(customer_id)
    
    return {
        "customer_id": customer_id,
        "assigned_segments": segments,
        "message": f"Customer assigned to {len(segments)} segments"
    }


@router.post("/recalculate")
async def recalculate_all_segments(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("crm", "update", "segments"))
):
    """Recalculate customer counts for all segments"""
    segment_service = SegmentService(session)
    return await segment_service.recalculate_all_segments()