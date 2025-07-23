"""
Tour instance management routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session, get_redis
from services.tour_instance_service import TourInstanceService
from schemas.tour_instance import (
    TourInstanceCreate, TourInstanceUpdate, TourInstanceResponse, TourInstanceSummary,
    TourAssignment, TourStatusUpdate, TourProgressUpdate, TourInstanceSearch
)
from models.tour_instance import TourStatus
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import redis
import uuid


router = APIRouter(prefix="/tour-instances", tags=["Tour Instances"])


@router.post("/", response_model=TourInstanceResponse)
async def create_tour_instance(
    instance_data: TourInstanceCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("tours", "create", "instances"))
):
    """Create a new tour instance"""
    instance_service = TourInstanceService(session, redis_client)
    return await instance_service.create_instance(instance_data)


@router.get("/", response_model=PaginatedResponse[TourInstanceResponse])
async def get_tour_instances(
    pagination: PaginationParams = Depends(),
    template_id: Optional[uuid.UUID] = Query(None, description="Filter by template ID"),
    booking_id: Optional[uuid.UUID] = Query(None, description="Filter by booking ID"),
    customer_id: Optional[uuid.UUID] = Query(None, description="Filter by customer ID"),
    status: Optional[TourStatus] = Query(None, description="Filter by status"),
    assigned_guide_id: Optional[uuid.UUID] = Query(None, description="Filter by assigned guide"),
    assigned_vehicle_id: Optional[uuid.UUID] = Query(None, description="Filter by assigned vehicle"),
    start_date_from: Optional[str] = Query(None, description="Filter by start date from (YYYY-MM-DD)"),
    start_date_to: Optional[str] = Query(None, description="Filter by start date to (YYYY-MM-DD)"),
    region: Optional[str] = Query(None, description="Filter by region"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("tours", "read", "instances"))
):
    """Get list of tour instances with optional search and filters"""
    instance_service = TourInstanceService(session, redis_client)
    
    # Build search criteria
    search = None
    if any([template_id, booking_id, customer_id, status, assigned_guide_id, 
            assigned_vehicle_id, start_date_from, start_date_to, region]):
        from datetime import datetime
        
        start_date_from_parsed = None
        start_date_to_parsed = None
        
        if start_date_from:
            start_date_from_parsed = datetime.strptime(start_date_from, "%Y-%m-%d").date()
        if start_date_to:
            start_date_to_parsed = datetime.strptime(start_date_to, "%Y-%m-%d").date()
        
        search = TourInstanceSearch(
            template_id=template_id,
            booking_id=booking_id,
            customer_id=customer_id,
            status=status,
            assigned_guide_id=assigned_guide_id,
            assigned_vehicle_id=assigned_vehicle_id,
            start_date_from=start_date_from_parsed,
            start_date_to=start_date_to_parsed,
            region=region
        )
    
    instances, total = await instance_service.get_instances(pagination, search)
    
    return PaginatedResponse.create(
        items=instances,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/active", response_model=List[TourInstanceResponse])
async def get_active_tours(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("tours", "read", "instances"))
):
    """Get all currently active tours"""
    instance_service = TourInstanceService(session, redis_client)
    return await instance_service.get_active_tours()


@router.get("/{instance_id}", response_model=TourInstanceResponse)
async def get_tour_instance(
    instance_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("tours", "read", "instances"))
):
    """Get tour instance by ID"""
    instance_service = TourInstanceService(session, redis_client)
    return await instance_service.get_instance(instance_id)


@router.get("/{instance_id}/summary", response_model=TourInstanceSummary)
async def get_tour_instance_summary(
    instance_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("tours", "read", "instances"))
):
    """Get comprehensive tour instance summary"""
    instance_service = TourInstanceService(session, redis_client)
    return await instance_service.get_instance_summary(instance_id)


@router.put("/{instance_id}", response_model=TourInstanceResponse)
async def update_tour_instance(
    instance_id: uuid.UUID,
    instance_data: TourInstanceUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("tours", "update", "instances"))
):
    """Update tour instance information"""
    instance_service = TourInstanceService(session, redis_client)
    return await instance_service.update_instance(instance_id, instance_data)


@router.post("/{instance_id}/assign", response_model=TourInstanceResponse)
async def assign_tour_resources(
    instance_id: uuid.UUID,
    assignment: TourAssignment,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("tours", "update", "instances"))
):
    """Assign guide, vehicle, and driver to tour instance"""
    instance_service = TourInstanceService(session, redis_client)
    return await instance_service.assign_resources(instance_id, assignment)


@router.post("/{instance_id}/status", response_model=TourInstanceResponse)
async def update_tour_status(
    instance_id: uuid.UUID,
    status_update: TourStatusUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("tours", "update", "instances"))
):
    """Update tour instance status"""
    instance_service = TourInstanceService(session, redis_client)
    return await instance_service.update_status(instance_id, status_update)


@router.post("/{instance_id}/progress", response_model=TourInstanceResponse)
async def update_tour_progress(
    instance_id: uuid.UUID,
    progress_update: TourProgressUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("tours", "update", "instances"))
):
    """Update tour progress"""
    instance_service = TourInstanceService(session, redis_client)
    return await instance_service.update_progress(instance_id, progress_update)