"""
Assignment management routes
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session
from database import get_session, get_redis
from services.assignment_service import AssignmentService
from schemas.assignment import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse
)
from models.assignment import AssignmentStatus
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import redis
import uuid
from datetime import date


router = APIRouter(prefix="/assignments", tags=["Assignment Management"])


@router.post("/", response_model=AssignmentResponse)
async def create_assignment(
    assignment_data: AssignmentCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "create", "assignments"))
):
    """Create a new vehicle assignment"""
    # Set assigned_by to current user if not provided
    if not assignment_data.assigned_by:
        assignment_data.assigned_by = current_user.user_id
    
    assignment_service = AssignmentService(session, redis_client)
    return await assignment_service.create_assignment(assignment_data)


@router.get("/", response_model=PaginatedResponse[AssignmentResponse])
async def get_assignments(
    pagination: PaginationParams = Depends(),
    vehicle_id: Optional[uuid.UUID] = Query(None, description="Filter by vehicle ID"),
    tour_instance_id: Optional[uuid.UUID] = Query(None, description="Filter by tour instance ID"),
    driver_id: Optional[uuid.UUID] = Query(None, description="Filter by driver ID"),
    status: Optional[AssignmentStatus] = Query(None, description="Filter by status"),
    start_date_from: Optional[str] = Query(None, description="Filter from start date (YYYY-MM-DD)"),
    start_date_to: Optional[str] = Query(None, description="Filter to start date (YYYY-MM-DD)"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "assignments"))
):
    """Get list of assignments with optional filters"""
    assignment_service = AssignmentService(session, redis_client)
    
    # Parse dates
    start_date_from_parsed = None
    start_date_to_parsed = None
    
    if start_date_from:
        try:
            start_date_from_parsed = date.fromisoformat(start_date_from)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date_from format. Use YYYY-MM-DD"
            )
    
    if start_date_to:
        try:
            start_date_to_parsed = date.fromisoformat(start_date_to)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date_to format. Use YYYY-MM-DD"
            )
    
    assignments, total = await assignment_service.get_assignments(
        pagination=pagination,
        vehicle_id=vehicle_id,
        tour_instance_id=tour_instance_id,
        driver_id=driver_id,
        status=status,
        start_date_from=start_date_from_parsed,
        start_date_to=start_date_to_parsed
    )
    
    return PaginatedResponse.create(
        items=assignments,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "assignments"))
):
    """Get assignment by ID"""
    assignment_service = AssignmentService(session, redis_client)
    return await assignment_service.get_assignment(assignment_id)


@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: uuid.UUID,
    assignment_data: AssignmentUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "update", "assignments"))
):
    """Update assignment information"""
    assignment_service = AssignmentService(session, redis_client)
    return await assignment_service.update_assignment(assignment_id, assignment_data)


@router.post("/{assignment_id}/cancel", response_model=AssignmentResponse)
async def cancel_assignment(
    assignment_id: uuid.UUID,
    reason: str = Query(..., description="Cancellation reason"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "update", "assignments"))
):
    """Cancel an assignment"""
    assignment_service = AssignmentService(session, redis_client)
    return await assignment_service.cancel_assignment(assignment_id, reason)


@router.post("/{assignment_id}/start", response_model=AssignmentResponse)
async def start_assignment(
    assignment_id: uuid.UUID,
    start_odometer: int = Query(..., description="Starting odometer reading"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "update", "assignments"))
):
    """Start an assignment (mark as active)"""
    assignment_service = AssignmentService(session, redis_client)
    return await assignment_service.start_assignment(assignment_id, start_odometer)


@router.post("/{assignment_id}/complete", response_model=AssignmentResponse)
async def complete_assignment(
    assignment_id: uuid.UUID,
    end_odometer: int = Query(..., description="Ending odometer reading"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "update", "assignments"))
):
    """Complete an assignment"""
    assignment_service = AssignmentService(session, redis_client)
    return await assignment_service.complete_assignment(assignment_id, end_odometer)


@router.get("/vehicle/{vehicle_id}", response_model=PaginatedResponse[AssignmentResponse])
async def get_vehicle_assignments(
    vehicle_id: uuid.UUID,
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "assignments"))
):
    """Get all assignments for a specific vehicle"""
    assignment_service = AssignmentService(session, redis_client)
    
    assignments, total = await assignment_service.get_vehicle_assignments(vehicle_id, pagination)
    
    return PaginatedResponse.create(
        items=assignments,
        total=total,
        page=pagination.page,
        size=pagination.size
    )