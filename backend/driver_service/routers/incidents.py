"""
Driver incident routes
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session
from database import get_session
from models.driver_incident import DriverIncident, IncidentType, IncidentSeverity, IncidentStatus
from schemas.driver_incident import (
    DriverIncidentCreate, DriverIncidentUpdate, DriverIncidentResponse
)
from utils.auth import get_current_user, require_permission, CurrentUser
from services.incident_service import IncidentService
from typing import List, Optional
from datetime import date
import uuid


router = APIRouter(prefix="/incidents", tags=["Driver Incidents"])


@router.post("/", response_model=DriverIncidentResponse)
async def create_incident(
    incident_data: DriverIncidentCreate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("incidents", "create", "all"))
):
    """Create a new incident report"""
    incident_service = IncidentService(session)
    return await incident_service.create_incident(incident_data, current_user.user_id)


@router.get("/", response_model=List[DriverIncidentResponse])
async def get_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    driver_id: Optional[uuid.UUID] = Query(None, description="Filter by driver ID"),
    incident_type: Optional[IncidentType] = Query(None, description="Filter by incident type"),
    severity: Optional[IncidentSeverity] = Query(None, description="Filter by severity"),
    status: Optional[IncidentStatus] = Query(None, description="Filter by status"),
    start_date: Optional[date] = Query(None, description="Filter incidents from this date"),
    end_date: Optional[date] = Query(None, description="Filter incidents until this date"),
    overdue_only: bool = Query(False, description="Show only overdue incidents"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("incidents", "read", "all"))
):
    """Get list of incidents with filtering"""
    incident_service = IncidentService(session)
    return await incident_service.get_incidents(
        skip=skip,
        limit=limit,
        driver_id=driver_id,
        incident_type=incident_type,
        severity=severity,
        status=status,
        start_date=start_date,
        end_date=end_date,
        overdue_only=overdue_only
    )


@router.get("/driver/{driver_id}", response_model=List[DriverIncidentResponse])
async def get_driver_incidents(
    driver_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    incident_type: Optional[IncidentType] = Query(None),
    severity: Optional[IncidentSeverity] = Query(None),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("incidents", "read", "all"))
):
    """Get incidents for a specific driver"""
    incident_service = IncidentService(session)
    return await incident_service.get_driver_incidents(
        driver_id=driver_id,
        skip=skip,
        limit=limit,
        incident_type=incident_type,
        severity=severity
    )


@router.get("/overdue", response_model=List[DriverIncidentResponse])
async def get_overdue_incidents(
    severity: Optional[IncidentSeverity] = Query(None),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("incidents", "read", "all"))
):
    """Get overdue incidents that need immediate attention"""
    incident_service = IncidentService(session)
    return await incident_service.get_overdue_incidents(severity)


@router.get("/critical", response_model=List[DriverIncidentResponse])
async def get_critical_incidents(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("incidents", "read", "all"))
):
    """Get critical incidents requiring immediate attention"""
    incident_service = IncidentService(session)
    return await incident_service.get_critical_incidents()


@router.get("/{incident_id}", response_model=DriverIncidentResponse)
async def get_incident(
    incident_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("incidents", "read", "all"))
):
    """Get incident by ID"""
    incident_service = IncidentService(session)
    return await incident_service.get_incident(incident_id)


@router.put("/{incident_id}", response_model=DriverIncidentResponse)
async def update_incident(
    incident_id: uuid.UUID,
    incident_data: DriverIncidentUpdate,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("incidents", "update", "all"))
):
    """Update incident information"""
    incident_service = IncidentService(session)
    return await incident_service.update_incident(incident_id, incident_data)


@router.put("/{incident_id}/investigate")
async def start_investigation(
    incident_id: uuid.UUID,
    investigation_notes: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("incidents", "investigate", "all"))
):
    """Start investigation of an incident"""
    incident_service = IncidentService(session)
    return await incident_service.start_investigation(
        incident_id=incident_id,
        investigated_by=current_user.user_id,
        investigation_notes=investigation_notes
    )


@router.put("/{incident_id}/resolve")
async def resolve_incident(
    incident_id: uuid.UUID,
    resolution_description: str,
    corrective_action: Optional[str] = None,
    preventive_measures: Optional[str] = None,
    actual_cost: Optional[float] = None,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("incidents", "resolve", "all"))
):
    """Resolve an incident"""
    incident_service = IncidentService(session)
    return await incident_service.resolve_incident(
        incident_id=incident_id,
        resolution_description=resolution_description,
        corrective_action=corrective_action,
        preventive_measures=preventive_measures,
        actual_cost=actual_cost,
        resolved_by=current_user.user_id
    )


@router.put("/{incident_id}/escalate")
async def escalate_incident(
    incident_id: uuid.UUID,
    escalation_reason: str,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("incidents", "escalate", "all"))
):
    """Escalate an incident"""
    incident_service = IncidentService(session)
    return await incident_service.escalate_incident(incident_id, escalation_reason)


@router.put("/{incident_id}/close")
async def close_incident(
    incident_id: uuid.UUID,
    closure_notes: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("incidents", "close", "all"))
):
    """Close an incident"""
    incident_service = IncidentService(session)
    return await incident_service.close_incident(incident_id, closure_notes)


@router.delete("/{incident_id}")
async def delete_incident(
    incident_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("incidents", "delete", "all"))
):
    """Delete an incident"""
    incident_service = IncidentService(session)
    return await incident_service.delete_incident(incident_id)


@router.get("/analytics/summary")
async def get_incident_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    driver_id: Optional[uuid.UUID] = Query(None),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("incidents", "read", "analytics"))
):
    """Get incident analytics and summary"""
    incident_service = IncidentService(session)
    return await incident_service.get_incident_analytics(
        start_date=start_date,
        end_date=end_date,
        driver_id=driver_id
    )


@router.get("/analytics/trends")
async def get_incident_trends(
    months: int = Query(12, ge=1, le=24, description="Number of months to analyze"),
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(require_permission("incidents", "read", "analytics"))
):
    """Get incident trends over time"""
    incident_service = IncidentService(session)
    return await incident_service.get_incident_trends(months)