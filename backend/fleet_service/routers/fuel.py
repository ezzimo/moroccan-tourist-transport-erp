"""
Fuel management routes
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session
from database import get_session
from services.fuel_service import FuelService
from schemas.fuel_log import (
    FuelLogCreate, FuelLogUpdate, FuelLogResponse, FuelStats
)
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import uuid
from datetime import date


router = APIRouter(prefix="/fuel", tags=["Fuel Management"])


@router.post("/", response_model=FuelLogResponse)
async def create_fuel_log(
    log_data: FuelLogCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("fleet", "create", "fuel"))
):
    """Create a new fuel log entry"""
    # Set created_by to current user if not provided
    if not log_data.created_by:
        log_data.created_by = current_user.user_id
    
    fuel_service = FuelService(session)
    return await fuel_service.create_fuel_log(log_data)


@router.get("/", response_model=PaginatedResponse[FuelLogResponse])
async def get_fuel_logs(
    pagination: PaginationParams = Depends(),
    vehicle_id: Optional[uuid.UUID] = Query(None, description="Filter by vehicle ID"),
    driver_id: Optional[uuid.UUID] = Query(None, description="Filter by driver ID"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "fuel"))
):
    """Get list of fuel logs with optional filters"""
    fuel_service = FuelService(session)
    
    # Parse dates
    date_from_parsed = None
    date_to_parsed = None
    
    if date_from:
        try:
            date_from_parsed = date.fromisoformat(date_from)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_from format. Use YYYY-MM-DD"
            )
    
    if date_to:
        try:
            date_to_parsed = date.fromisoformat(date_to)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_to format. Use YYYY-MM-DD"
            )
    
    logs, total = await fuel_service.get_fuel_logs(
        pagination=pagination,
        vehicle_id=vehicle_id,
        driver_id=driver_id,
        date_from=date_from_parsed,
        date_to=date_to_parsed
    )
    
    return PaginatedResponse.create(
        items=logs,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/stats", response_model=FuelStats)
async def get_fuel_stats(
    days: int = Query(365, ge=1, le=1095, description="Number of days for statistics"),
    vehicle_id: Optional[uuid.UUID] = Query(None, description="Filter by vehicle ID"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "fuel"))
):
    """Get fuel consumption statistics"""
    fuel_service = FuelService(session)
    return await fuel_service.get_fuel_stats(days, vehicle_id)


@router.get("/{log_id}", response_model=FuelLogResponse)
async def get_fuel_log(
    log_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "fuel"))
):
    """Get fuel log by ID"""
    fuel_service = FuelService(session)
    return await fuel_service.get_fuel_log(log_id)


@router.put("/{log_id}", response_model=FuelLogResponse)
async def update_fuel_log(
    log_id: uuid.UUID,
    log_data: FuelLogUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("fleet", "update", "fuel"))
):
    """Update fuel log information"""
    fuel_service = FuelService(session)
    return await fuel_service.update_fuel_log(log_id, log_data)


@router.delete("/{log_id}")
async def delete_fuel_log(
    log_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("fleet", "delete", "fuel"))
):
    """Delete fuel log"""
    fuel_service = FuelService(session)
    return await fuel_service.delete_fuel_log(log_id)


@router.get("/vehicle/{vehicle_id}", response_model=PaginatedResponse[FuelLogResponse])
async def get_vehicle_fuel_history(
    vehicle_id: uuid.UUID,
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "fuel"))
):
    """Get fuel history for a specific vehicle"""
    fuel_service = FuelService(session)
    
    logs, total = await fuel_service.get_vehicle_fuel_history(vehicle_id, pagination)
    
    return PaginatedResponse.create(
        items=logs,
        total=total,
        page=pagination.page,
        size=pagination.size
    )