"""
Vehicle management routes
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session
from database import get_session, get_redis
from services.vehicle_service import VehicleService
from schemas.vehicle import (
    VehicleCreate, VehicleUpdate, VehicleResponse, VehicleSummary, 
    VehicleSearch, VehicleAvailability
)
from models.vehicle import VehicleType, VehicleStatus, FuelType
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import redis
import uuid
from datetime import date


router = APIRouter(prefix="/vehicles", tags=["Vehicle Management"])


@router.post("/", response_model=VehicleResponse)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission(
            "fleet",
            "create",
            "vehicles",
        )
    )
):
    """Create a new vehicle"""
    vehicle_service = VehicleService(session, redis_client)
    return await vehicle_service.create_vehicle(vehicle_data)


@router.get("/", response_model=PaginatedResponse[VehicleResponse])
async def get_vehicles(
    pagination: PaginationParams = Depends(),
    query: Optional[str] = Query(None, description="Search query"),
    vehicle_type: Optional[VehicleType] = Query(None, description="Filter by vehicle type"),
    status: Optional[VehicleStatus] = Query(None, description="Filter by status"),
    fuel_type: Optional[FuelType] = Query(None, description="Filter by fuel type"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_seating_capacity: Optional[int] = Query(None, description="Minimum seating capacity"),
    max_seating_capacity: Optional[int] = Query(None, description="Maximum seating capacity"),
    min_year: Optional[int] = Query(None, description="Minimum year"),
    max_year: Optional[int] = Query(None, description="Maximum year"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    available_from: Optional[str] = Query(None, description="Available from date (YYYY-MM-DD)"),
    available_to: Optional[str] = Query(None, description="Available to date (YYYY-MM-DD)"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "vehicles"))
):
    """Get list of vehicles with optional search and filters"""
    vehicle_service = VehicleService(session, redis_client)
    
    # Build search criteria
    search = None
    if any([query, vehicle_type, status, fuel_type, brand, min_seating_capacity, 
            max_seating_capacity, min_year, max_year, is_active is not None, 
            available_from, available_to]):
        
        available_from_parsed = None
        available_to_parsed = None
        
        if available_from:
            try:
                available_from_parsed = date.fromisoformat(available_from)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid available_from date format. Use YYYY-MM-DD"
                )
        
        if available_to:
            try:
                available_to_parsed = date.fromisoformat(available_to)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid available_to date format. Use YYYY-MM-DD"
                )
        
        search = VehicleSearch(
            query=query,
            vehicle_type=vehicle_type,
            status=status,
            fuel_type=fuel_type,
            brand=brand,
            min_seating_capacity=min_seating_capacity,
            max_seating_capacity=max_seating_capacity,
            min_year=min_year,
            max_year=max_year,
            is_active=is_active,
            available_from=available_from_parsed,
            available_to=available_to_parsed
        )
    
    vehicles, total = await vehicle_service.get_vehicles(pagination, search)
    
    return PaginatedResponse.create(
        items=vehicles,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/available", response_model=List[VehicleResponse])
async def get_available_vehicles(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    vehicle_type: Optional[VehicleType] = Query(None, description="Filter by vehicle type"),
    min_seating_capacity: Optional[int] = Query(None, description="Minimum seating capacity"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "vehicles"))
):
    """Get available vehicles for a specific period"""
    try:
        start_date_parsed = date.fromisoformat(start_date)
        end_date_parsed = date.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    if end_date_parsed < start_date_parsed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    vehicle_service = VehicleService(session, redis_client)
    return await vehicle_service.get_available_vehicles(
        start_date_parsed, 
        end_date_parsed, 
        vehicle_type.value if vehicle_type else None,
        min_seating_capacity
    )


@router.get("/compliance-alerts", response_model=List[dict])
async def get_compliance_alerts(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "vehicles"))
):
    """Get vehicles with upcoming compliance deadlines"""
    vehicle_service = VehicleService(session, redis_client)
    return await vehicle_service.check_compliance_alerts()


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "vehicles"))
):
    """Get vehicle by ID"""
    vehicle_service = VehicleService(session, redis_client)
    return await vehicle_service.get_vehicle(vehicle_id)


@router.get("/{vehicle_id}/summary", response_model=VehicleSummary)
async def get_vehicle_summary(
    vehicle_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "vehicles"))
):
    """Get comprehensive vehicle summary"""
    vehicle_service = VehicleService(session, redis_client)
    return await vehicle_service.get_vehicle_summary(vehicle_id)


@router.get("/{vehicle_id}/availability", response_model=VehicleAvailability)
async def check_vehicle_availability(
    vehicle_id: uuid.UUID,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "read", "vehicles"))
):
    """Check vehicle availability for a specific period"""
    try:
        start_date_parsed = date.fromisoformat(start_date)
        end_date_parsed = date.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    vehicle_service = VehicleService(session, redis_client)
    return await vehicle_service.check_availability(vehicle_id, start_date_parsed, end_date_parsed)


@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: uuid.UUID,
    vehicle_data: VehicleUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "update", "vehicles"))
):
    """Update vehicle information"""
    vehicle_service = VehicleService(session, redis_client)
    return await vehicle_service.update_vehicle(vehicle_id, vehicle_data)


@router.delete("/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("fleet", "delete", "vehicles"))
):
    """Delete vehicle (soft delete)"""
    vehicle_service = VehicleService(session, redis_client)
    return await vehicle_service.delete_vehicle(vehicle_id)