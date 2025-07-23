"""
Maintenance management routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session, get_redis
from services.maintenance_service import MaintenanceService
from schemas.maintenance_record import (
    MaintenanceRecordCreate, MaintenanceRecordUpdate, MaintenanceRecordResponse, MaintenanceStats
)
from models.maintenance_record import MaintenanceType
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import redis
import uuid
from datetime import date


router = APIRouter(prefix="/maintenance", tags=["Maintenance Management"])


@router.post("/", response_model=MaintenanceRecordResponse)
async def create_maintenance_record(
    record_data: MaintenanceRecordCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "create", "maintenance"))
):
    """Create a new maintenance record"""
    # Set performed_by to current user if not provided
    if not record_data.performed_by:
        record_data.performed_by = current_user.user_id
    
    maintenance_service = MaintenanceService(session, redis_client)
    return await maintenance_service.create_maintenance_record(record_data)


@router.get("/", response_model=PaginatedResponse[MaintenanceRecordResponse])
async def get_maintenance_records(
    pagination: PaginationParams = Depends(),
    vehicle_id: Optional[uuid.UUID] = Query(None, description="Filter by vehicle ID"),
    maintenance_type: Optional[MaintenanceType] = Query(None, description="Filter by maintenance type"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    is_completed: Optional[bool] = Query(None, description="Filter by completion status"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "maintenance"))
):
    """Get list of maintenance records with optional filters"""
    maintenance_service = MaintenanceService(session, redis_client)
    
    # Parse dates
    date_from_parsed = None
    date_to_parsed = None
    
    if date_from:
        try:
            date_from_parsed = date.fromisoformat(date_from)
        except ValueError:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_from format. Use YYYY-MM-DD"
            )
    
    if date_to:
        try:
            date_to_parsed = date.fromisoformat(date_to)
        except ValueError:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_to format. Use YYYY-MM-DD"
            )
    
    records, total = await maintenance_service.get_maintenance_records(
        pagination=pagination,
        vehicle_id=vehicle_id,
        maintenance_type=maintenance_type,
        date_from=date_from_parsed,
        date_to=date_to_parsed,
        is_completed=is_completed
    )
    
    return PaginatedResponse.create(
        items=records,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/upcoming", response_model=List[dict])
async def get_upcoming_maintenance(
    days_ahead: int = Query(30, ge=1, le=365, description="Days ahead to check"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "maintenance"))
):
    """Get vehicles with upcoming maintenance"""
    maintenance_service = MaintenanceService(session, redis_client)
    return await maintenance_service.get_upcoming_maintenance(days_ahead)


@router.get("/stats", response_model=MaintenanceStats)
async def get_maintenance_stats(
    days: int = Query(365, ge=1, le=1095, description="Number of days for statistics"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "maintenance"))
):
    """Get maintenance statistics"""
    maintenance_service = MaintenanceService(session, redis_client)
    return await maintenance_service.get_maintenance_stats(days)


@router.get("/{record_id}", response_model=MaintenanceRecordResponse)
async def get_maintenance_record(
    record_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "maintenance"))
):
    """Get maintenance record by ID"""
    maintenance_service = MaintenanceService(session, redis_client)
    return await maintenance_service.get_maintenance_record(record_id)


@router.put("/{record_id}", response_model=MaintenanceRecordResponse)
async def update_maintenance_record(
    record_id: uuid.UUID,
    record_data: MaintenanceRecordUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "update", "maintenance"))
):
    """Update maintenance record information"""
    maintenance_service = MaintenanceService(session, redis_client)
    return await maintenance_service.update_maintenance_record(record_id, record_data)


@router.delete("/{record_id}")
async def delete_maintenance_record(
    record_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "delete", "maintenance"))
):
    """Delete maintenance record"""
    maintenance_service = MaintenanceService(session, redis_client)
    return await maintenance_service.delete_maintenance_record(record_id)


@router.get("/vehicle/{vehicle_id}", response_model=PaginatedResponse[MaintenanceRecordResponse])
async def get_vehicle_maintenance_history(
    vehicle_id: uuid.UUID,
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "maintenance"))
):
    """Get maintenance history for a specific vehicle"""
    maintenance_service = MaintenanceService(session, redis_client)
    
    records, total = await maintenance_service.get_vehicle_maintenance_history(vehicle_id, pagination)
    
    return PaginatedResponse.create(
        items=records,
        total=total,
        page=pagination.page,
        size=pagination.size
    )