"""
Non-conformity management routes
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session, get_redis
from services.nonconformity_service import NonConformityService
from schemas.nonconformity import (
    NonConformityCreate, NonConformityUpdate, NonConformityResponse,
    NonConformitySummary, NonConformityResolution, NonConformityVerification
)
from models.nonconformity import Severity, NCStatus
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional, Dict, Any
import redis
import uuid


router = APIRouter(prefix="/nonconformities", tags=["Non-Conformity Management"])


@router.post("/", response_model=NonConformityResponse)
async def create_nonconformity(
    nc_data: NonConformityCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "create", "nonconformities"))
):
    """Create a new non-conformity"""
    nc_service = NonConformityService(session, redis_client)
    return await nc_service.create_nonconformity(nc_data)


@router.get("/", response_model=PaginatedResponse[NonConformityResponse])
async def get_nonconformities(
    pagination: PaginationParams = Depends(),
    audit_id: Optional[uuid.UUID] = Query(None, description="Filter by audit"),
    severity: Optional[Severity] = Query(None, description="Filter by severity"),
    status: Optional[NCStatus] = Query(None, description="Filter by status"),
    assigned_to: Optional[uuid.UUID] = Query(None, description="Filter by assignee"),
    overdue_only: Optional[bool] = Query(None, description="Show only overdue items"),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "nonconformities"))
):
    """Get list of non-conformities with optional filters"""
    nc_service = NonConformityService(session, redis_client)
    
    nonconformities, total = await nc_service.get_nonconformities(
        pagination=pagination,
        audit_id=audit_id,
        severity=severity,
        status=status,
        assigned_to=assigned_to,
        overdue_only=overdue_only
    )
    
    return PaginatedResponse.create(
        items=nonconformities,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/summary", response_model=NonConformitySummary)
async def get_nonconformity_summary(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "nonconformities"))
):
    """Get non-conformity summary statistics"""
    nc_service = NonConformityService(session, redis_client)
    return await nc_service.get_nonconformity_summary()


@router.get("/overdue", response_model=List[NonConformityResponse])
async def get_overdue_nonconformities(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "nonconformities"))
):
    """Get all overdue non-conformities"""
    nc_service = NonConformityService(session, redis_client)
    return await nc_service.get_overdue_nonconformities()


@router.get("/{nc_id}", response_model=NonConformityResponse)
async def get_nonconformity(
    nc_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "nonconformities"))
):
    """Get non-conformity by ID"""
    nc_service = NonConformityService(session, redis_client)
    return await nc_service.get_nonconformity(nc_id)


@router.put("/{nc_id}", response_model=NonConformityResponse)
async def update_nonconformity(
    nc_id: uuid.UUID,
    nc_data: NonConformityUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "update", "nonconformities"))
):
    """Update non-conformity information"""
    nc_service = NonConformityService(session, redis_client)
    return await nc_service.update_nonconformity(nc_id, nc_data)


@router.post("/{nc_id}/resolve", response_model=NonConformityResponse)
async def resolve_nonconformity(
    nc_id: uuid.UUID,
    resolution: NonConformityResolution,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "update", "nonconformities"))
):
    """Resolve a non-conformity"""
    nc_service = NonConformityService(session, redis_client)
    return await nc_service.resolve_nonconformity(nc_id, resolution, current_user.user_id)


@router.post("/{nc_id}/verify", response_model=NonConformityResponse)
async def verify_nonconformity(
    nc_id: uuid.UUID,
    verification: NonConformityVerification,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "verify", "nonconformities"))
):
    """Verify non-conformity resolution"""
    nc_service = NonConformityService(session, redis_client)
    return await nc_service.verify_nonconformity(nc_id, verification, current_user.user_id)


@router.delete("/{nc_id}")
async def delete_nonconformity(
    nc_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "delete", "nonconformities"))
):
    """Delete non-conformity"""
    nc_service = NonConformityService(session, redis_client)
    return await nc_service.delete_nonconformity(nc_id)


@router.get("/audit/{audit_id}", response_model=List[NonConformityResponse])
async def get_audit_nonconformities(
    audit_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(require_permission("qa", "read", "nonconformities"))
):
    """Get all non-conformities for a specific audit"""
    nc_service = NonConformityService(session, redis_client)
    return await nc_service.get_audit_nonconformities(audit_id)