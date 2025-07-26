"""
Driver assignment routes
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session
from database import get_session
from models.driver_assignment import DriverAssignment, AssignmentStatus
from schemas.driver_assignment import (
    DriverAssignmentCreate, DriverAssignmentUpdate, DriverAssignmentResponse
)
from utils.auth import get_current_user, require_permission, CurrentUser
from services.assignment_service import AssignmentService
from typing import List, Optional
from datetime import date
import uuid


router = APIRouter(prefix="/assignments", tags=["Driver Assignments"])


@router.post("/", response_model=DriverAssignmentResponse)
async def create_assignment(
    assignment_data: DriverAssignmentCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("assignments", "create", "all"))
):
    """Create a new driver assignment"""
    assignment_service = AssignmentService(session)
    return await assignment_service.create_assignment(assignment_data, current_user.user_id)


@router.get("/", response_model=List[DriverAssignmentResponse])
async def get_assignments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    driver_id: Optional[uuid.UUID] = Query(None, description="Filter by driver ID"),
    status: Optional[AssignmentStatus] = Query(None, description="Filter by assignment status"),
    start_date: Optional[date] = Query(None, description="Filter assignments starting from this date"),
    end_date: Optional[date] = Query(None, description="Filter assignments ending before this date"),
    active_only: bool = Query(False, description="Show only active assignments"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("assignments", "read", "all"))
):
    """Get list of driver assignments with filtering"""
    assignment_service = AssignmentService(session)
    return await assignment_service.get_assignments(
        skip=skip,
        limit=limit,
        driver_id=driver_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        active_only=active_only
    )


@router.get("/conflicts", response_model=List[DriverAssignmentResponse])
async def get_assignment_conflicts(
    driver_id: uuid.UUID,
    start_date: date,
    end_date: date,
    exclude_assignment_id: Optional[uuid.UUID] = Query(None, description="Assignment ID to exclude from conflict check"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("assignments", "read", "all"))
):
    """Check for assignment conflicts for a driver in a date range"""
    assignment_service = AssignmentService(session)
    return await assignment_service.check_conflicts(
        driver_id=driver_id,
        start_date=start_date,
        end_date=end_date,
        exclude_assignment_id=exclude_assignment_id
    )


@router.get("/driver/{driver_id}", response_model=List[DriverAssignmentResponse])
async def get_driver_assignments(
    driver_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[AssignmentStatus] = Query(None),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("assignments", "read", "all"))
):
    """Get assignments for a specific driver"""
    assignment_service = AssignmentService(session)
    return await assignment_service.get_driver_assignments(
        driver_id=driver_id,
        skip=skip,
        limit=limit,
        status=status
    )


@router.get("/{assignment_id}", response_model=DriverAssignmentResponse)
async def get_assignment(
    assignment_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("assignments", "read", "all"))
):
    """Get assignment by ID"""
    assignment_service = AssignmentService(session)
    return await assignment_service.get_assignment(assignment_id)


@router.put("/{assignment_id}", response_model=DriverAssignmentResponse)
async def update_assignment(
    assignment_id: uuid.UUID,
    assignment_data: DriverAssignmentUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("assignments", "update", "all"))
):
    """Update assignment information"""
    assignment_service = AssignmentService(session)
    return await assignment_service.update_assignment(assignment_id, assignment_data)


@router.put("/{assignment_id}/confirm")
async def confirm_assignment(
    assignment_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("assignments", "update", "all"))
):
    """Confirm an assignment"""
    assignment_service = AssignmentService(session)
    return await assignment_service.confirm_assignment(assignment_id)


@router.put("/{assignment_id}/start")
async def start_assignment(
    assignment_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("assignments", "update", "all"))
):
    """Start an assignment"""
    assignment_service = AssignmentService(session)
    return await assignment_service.start_assignment(assignment_id)


@router.put("/{assignment_id}/complete")
async def complete_assignment(
    assignment_id: uuid.UUID,
    customer_rating: Optional[float] = None,
    customer_feedback: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("assignments", "update", "all"))
):
    """Complete an assignment with optional feedback"""
    assignment_service = AssignmentService(session)
    return await assignment_service.complete_assignment(
        assignment_id=assignment_id,
        customer_rating=customer_rating,
        customer_feedback=customer_feedback
    )


@router.put("/{assignment_id}/cancel")
async def cancel_assignment(
    assignment_id: uuid.UUID,
    reason: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("assignments", "update", "all"))
):
    """Cancel an assignment"""
    assignment_service = AssignmentService(session)
    return await assignment_service.cancel_assignment(assignment_id, reason)


@router.delete("/{assignment_id}")
async def delete_assignment(
    assignment_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("assignments", "delete", "all"))
):
    """Delete an assignment"""
    assignment_service = AssignmentService(session)
    return await assignment_service.delete_assignment(assignment_id)


@router.get("/analytics/performance")
async def get_assignment_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    driver_id: Optional[uuid.UUID] = Query(None),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("assignments", "read", "analytics"))
):
    """Get assignment performance analytics"""
    assignment_service = AssignmentService(session)
    return await assignment_service.get_assignment_analytics(
        start_date=start_date,
        end_date=end_date,
        driver_id=driver_id
    )