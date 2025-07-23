"""
Availability management routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session
from services.availability_service import AvailabilityService
from schemas.availability import (
    AvailabilityRequest, AvailabilityResponse, AvailabilitySlotCreate,
    AvailabilitySlotUpdate, AvailabilitySlotResponse
)
from models.availability import ResourceType
from utils.auth import require_permission, CurrentUser
from typing import List, Optional, Dict, Any
from datetime import date
import uuid


router = APIRouter(prefix="/availability", tags=["Availability Management"])


@router.post("/check", response_model=AvailabilityResponse)
async def check_availability(
    request: AvailabilityRequest,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "read", "availability"))
):
    """Check availability for resources"""
    availability_service = AvailabilityService(session)
    return await availability_service.check_availability(request)


@router.post("/slots", response_model=AvailabilitySlotResponse)
async def create_availability_slot(
    slot_data: AvailabilitySlotCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "create", "availability"))
):
    """Create a new availability slot"""
    availability_service = AvailabilityService(session)
    return await availability_service.create_availability_slot(slot_data)


@router.put("/slots/{slot_id}", response_model=AvailabilitySlotResponse)
async def update_availability_slot(
    slot_id: uuid.UUID,
    slot_data: AvailabilitySlotUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "update", "availability"))
):
    """Update an availability slot"""
    availability_service = AvailabilityService(session)
    return await availability_service.update_availability_slot(slot_id, slot_data)


@router.post("/reserve")
async def reserve_capacity(
    resource_id: uuid.UUID,
    date: date,
    capacity: int,
    booking_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "update", "availability"))
):
    """Reserve capacity for a booking"""
    availability_service = AvailabilityService(session)
    success = await availability_service.reserve_capacity(resource_id, date, capacity, booking_id)
    
    return {
        "success": success,
        "message": "Capacity reserved successfully" if success else "Failed to reserve capacity"
    }


@router.post("/release")
async def release_capacity(
    resource_id: uuid.UUID,
    date: date,
    capacity: int,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "update", "availability"))
):
    """Release reserved capacity"""
    availability_service = AvailabilityService(session)
    success = await availability_service.release_capacity(resource_id, date, capacity)
    
    return {
        "success": success,
        "message": "Capacity released successfully" if success else "Failed to release capacity"
    }


@router.get("/schedule/{resource_id}", response_model=List[AvailabilitySlotResponse])
async def get_resource_schedule(
    resource_id: uuid.UUID,
    start_date: date = Query(..., description="Start date for schedule"),
    end_date: date = Query(..., description="End date for schedule"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "read", "availability"))
):
    """Get schedule for a specific resource"""
    availability_service = AvailabilityService(session)
    return await availability_service.get_resource_schedule(resource_id, start_date, end_date)


@router.post("/block/{resource_id}", response_model=List[AvailabilitySlotResponse])
async def block_resource(
    resource_id: uuid.UUID,
    start_date: date = Query(..., description="Start date for blocking"),
    end_date: date = Query(..., description="End date for blocking"),
    reason: str = Query(..., description="Reason for blocking"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "update", "availability"))
):
    """Block a resource for a date range"""
    availability_service = AvailabilityService(session)
    return await availability_service.block_resource(resource_id, start_date, end_date, reason)


@router.post("/unblock/{resource_id}", response_model=List[AvailabilitySlotResponse])
async def unblock_resource(
    resource_id: uuid.UUID,
    start_date: date = Query(..., description="Start date for unblocking"),
    end_date: date = Query(..., description="End date for unblocking"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "update", "availability"))
):
    """Unblock a resource for a date range"""
    availability_service = AvailabilityService(session)
    return await availability_service.unblock_resource(resource_id, start_date, end_date)


@router.get("/summary", response_model=Dict[str, Any])
async def get_availability_summary(
    start_date: date = Query(..., description="Start date for summary"),
    end_date: date = Query(..., description="End date for summary"),
    resource_type: Optional[ResourceType] = Query(None, description="Filter by resource type"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("booking", "read", "availability"))
):
    """Get availability summary for a date range"""
    availability_service = AvailabilityService(session)
    return await availability_service.get_availability_summary(start_date, end_date, resource_type)