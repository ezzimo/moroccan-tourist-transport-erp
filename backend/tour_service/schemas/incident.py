"""
Incident-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from models.incident import IncidentType, SeverityLevel
import uuid


class IncidentBase(BaseModel):
    incident_type: IncidentType
    severity: SeverityLevel
    title: str
    description: str
    location: Optional[str] = None
    day_number: Optional[int] = None
    affected_participants: Optional[int] = None
    estimated_delay_minutes: Optional[int] = None
    financial_impact: Optional[float] = None


class IncidentCreate(IncidentBase):
    tour_instance_id: uuid.UUID
    reporter_id: uuid.UUID
    
    @validator('day_number')
    def validate_day_number(cls, v):
        if v is not None and v < 1:
            raise ValueError('Day number must be at least 1')
        return v
    
    @validator('affected_participants')
    def validate_affected_participants(cls, v):
        if v is not None and v < 0:
            raise ValueError('Affected participants must be non-negative')
        return v
    
    @validator('estimated_delay_minutes')
    def validate_delay(cls, v):
        if v is not None and v < 0:
            raise ValueError('Estimated delay must be non-negative')
        return v


class IncidentUpdate(BaseModel):
    incident_type: Optional[IncidentType] = None
    severity: Optional[SeverityLevel] = None
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    day_number: Optional[int] = None
    affected_participants: Optional[int] = None
    estimated_delay_minutes: Optional[int] = None
    financial_impact: Optional[float] = None
    is_resolved: Optional[bool] = None
    resolution_description: Optional[str] = None
    resolved_by: Optional[uuid.UUID] = None
    requires_follow_up: Optional[bool] = None
    follow_up_notes: Optional[str] = None
    escalated_to: Optional[uuid.UUID] = None


class IncidentResponse(IncidentBase):
    id: uuid.UUID
    tour_instance_id: uuid.UUID
    reporter_id: uuid.UUID
    is_resolved: bool
    resolution_description: Optional[str]
    resolved_by: Optional[uuid.UUID]
    resolved_at: Optional[datetime]
    requires_follow_up: bool
    follow_up_notes: Optional[str]
    escalated_to: Optional[uuid.UUID]
    reported_at: datetime
    created_at: datetime
    updated_at: Optional[datetime]
    priority_score: int
    is_urgent: bool


class IncidentResolution(BaseModel):
    """Schema for incident resolution"""
    resolution_description: str
    resolved_by: uuid.UUID
    requires_follow_up: bool = False
    follow_up_notes: Optional[str] = None


class IncidentEscalation(BaseModel):
    """Schema for incident escalation"""
    escalated_to: uuid.UUID
    escalation_reason: str
    notes: Optional[str] = None


class IncidentStats(BaseModel):
    """Incident statistics"""
    total_incidents: int
    resolved_incidents: int
    unresolved_incidents: int
    by_type: dict
    by_severity: dict
    by_tour: dict
    average_resolution_time_hours: Optional[float]
    urgent_incidents: int
    incidents_requiring_follow_up: int


class IncidentSearch(BaseModel):
    """Incident search criteria"""
    tour_instance_id: Optional[uuid.UUID] = None
    incident_type: Optional[IncidentType] = None
    severity: Optional[SeverityLevel] = None
    is_resolved: Optional[bool] = None
    reporter_id: Optional[uuid.UUID] = None
    resolved_by: Optional[uuid.UUID] = None
    reported_from: Optional[datetime] = None
    reported_to: Optional[datetime] = None
    requires_follow_up: Optional[bool] = None
    is_urgent: Optional[bool] = None