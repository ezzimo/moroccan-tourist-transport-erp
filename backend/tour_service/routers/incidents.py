"""
Incident management routes
"""

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session, get_redis
from services.incident_service import IncidentService
from schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    IncidentResolution,
    IncidentEscalation,
    IncidentStats,
    IncidentSearch,
)
from models.incident import IncidentType, SeverityLevel
from utils.auth import require_permission, CurrentUser
from utils.pagination import PaginationParams, PaginatedResponse
from typing import List, Optional
import redis
import uuid


router = APIRouter(prefix="/incidents", tags=["Incident Management"])


@router.post("/", response_model=IncidentResponse)
async def create_incident(
    incident_data: IncidentCreate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("tours", "create", "incidents")
    ),
):
    """Create a new incident"""
    # Set reporter ID from current user if not provided
    if not incident_data.reporter_id:
        incident_data.reporter_id = current_user.user_id

    incident_service = IncidentService(session, redis_client)
    return await incident_service.create_incident(incident_data)


@router.get("/", response_model=PaginatedResponse[IncidentResponse])
async def get_incidents(
    pagination: PaginationParams = Depends(),
    tour_instance_id: Optional[uuid.UUID] = Query(
        None, description="Filter by tour instance ID"
    ),
    incident_type: Optional[IncidentType] = Query(
        None, description="Filter by incident type"
    ),
    severity: Optional[SeverityLevel] = Query(
        None, description="Filter by severity"
    ),
    is_resolved: Optional[bool] = Query(
        None, description="Filter by resolution status"
    ),
    reporter_id: Optional[uuid.UUID] = Query(
        None, description="Filter by reporter ID"
    ),
    resolved_by: Optional[uuid.UUID] = Query(
        None, description="Filter by resolver ID"
    ),
    requires_follow_up: Optional[bool] = Query(
        None, description="Filter by follow-up requirement"
    ),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("tours", "read", "incidents")
    ),
):
    """Get list of incidents with optional filters"""
    incident_service = IncidentService(session, redis_client)

    # Build search criteria
    search = None
    if any(
        [
            tour_instance_id,
            incident_type,
            severity,
            is_resolved is not None,
            reporter_id,
            resolved_by,
            requires_follow_up is not None,
        ]
    ):
        search = IncidentSearch(
            tour_instance_id=tour_instance_id,
            incident_type=incident_type,
            severity=severity,
            is_resolved=is_resolved,
            reporter_id=reporter_id,
            resolved_by=resolved_by,
            requires_follow_up=requires_follow_up,
        )

    incidents, total = await incident_service.get_incidents(pagination, search)

    return PaginatedResponse.create(
        items=incidents,
        total=total,
        page=pagination.page,
        size=pagination.size
    )


@router.get("/urgent", response_model=List[IncidentResponse])
async def get_urgent_incidents(
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("tours", "read", "incidents")
    ),
):
    """Get all urgent unresolved incidents"""
    incident_service = IncidentService(session, redis_client)
    return await incident_service.get_urgent_incidents()


@router.get("/stats", response_model=IncidentStats)
async def get_incident_stats(
    days: int = Query(
        30,
        ge=1,
        le=365,
        description="Number of days for statistics",
    ),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("tours", "read", "incidents")
    ),
):
    """Get incident statistics"""
    incident_service = IncidentService(session, redis_client)
    return await incident_service.get_incident_stats(days)


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: uuid.UUID,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("tours", "read", "incidents")
    ),
):
    """Get incident by ID"""
    incident_service = IncidentService(session, redis_client)
    return await incident_service.get_incident(incident_id)


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: uuid.UUID,
    incident_data: IncidentUpdate,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("tours", "update", "incidents")
    ),
):
    """Update incident information"""
    incident_service = IncidentService(session, redis_client)
    return await incident_service.update_incident(incident_id, incident_data)


@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve_incident(
    incident_id: uuid.UUID,
    resolution_data: IncidentResolution,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("tours", "update", "incidents")
    ),
):
    """Resolve an incident"""
    # Set resolved_by to current user if not provided
    if not resolution_data.resolved_by:
        resolution_data.resolved_by = current_user.user_id

    incident_service = IncidentService(session, redis_client)
    return await incident_service.resolve_incident(
        incident_id,
        resolution_data,
    )


@router.post("/{incident_id}/escalate", response_model=IncidentResponse)
async def escalate_incident(
    incident_id: uuid.UUID,
    escalation_data: IncidentEscalation,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("tours", "update", "incidents")
    ),
):
    """Escalate an incident"""
    incident_service = IncidentService(session, redis_client)
    return await incident_service.escalate_incident(
        incident_id,
        escalation_data,
    )


@router.get(
    "/tour/{tour_instance_id}",
    response_model=PaginatedResponse[IncidentResponse],
)
async def get_tour_incidents(
    tour_instance_id: uuid.UUID,
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: CurrentUser = Depends(
        require_permission("tours", "read", "incidents")
    ),
):
    """Get all incidents for a specific tour"""
    incident_service = IncidentService(session, redis_client)

    incidents, total = await incident_service.get_tour_incidents(
        tour_instance_id, pagination
    )

    return PaginatedResponse.create(
        items=incidents,
        total=total,
        page=pagination.page,
        size=pagination.size,
    )
