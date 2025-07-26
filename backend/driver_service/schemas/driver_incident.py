"""
Driver incident-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime, date
from models.driver_incident import IncidentType, IncidentSeverity, IncidentStatus
import uuid


class DriverIncidentBase(BaseModel):
    incident_type: IncidentType
    severity: IncidentSeverity
    title: str
    description: str
    incident_date: date
    incident_time: Optional[datetime] = None
    location: Optional[str] = None
    witness_names: Optional[str] = None
    customer_involved: bool = False
    customer_name: Optional[str] = None
    customer_contact: Optional[str] = None
    estimated_cost: Optional[float] = None
    insurance_claim: bool = False
    claim_number: Optional[str] = None
    police_report_filed: bool = False
    police_report_number: Optional[str] = None
    photos_taken: bool = False


class DriverIncidentCreate(DriverIncidentBase):
    driver_id: uuid.UUID
    assignment_id: Optional[uuid.UUID] = None


class DriverIncidentUpdate(BaseModel):
    incident_type: Optional[IncidentType] = None
    severity: Optional[IncidentSeverity] = None
    title: Optional[str] = None
    description: Optional[str] = None
    incident_date: Optional[date] = None
    incident_time: Optional[datetime] = None
    location: Optional[str] = None
    witness_names: Optional[str] = None
    customer_involved: Optional[bool] = None
    customer_name: Optional[str] = None
    customer_contact: Optional[str] = None
    status: Optional[IncidentStatus] = None
    investigation_notes: Optional[str] = None
    resolution_description: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_measures: Optional[str] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    insurance_claim: Optional[bool] = None
    claim_number: Optional[str] = None
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[date] = None
    follow_up_notes: Optional[str] = None
    police_report_filed: Optional[bool] = None
    police_report_number: Optional[str] = None
    photos_taken: Optional[bool] = None


class DriverIncidentResponse(DriverIncidentBase):
    id: uuid.UUID
    driver_id: uuid.UUID
    assignment_id: Optional[uuid.UUID]
    reported_by: uuid.UUID
    reported_at: datetime
    status: IncidentStatus
    investigated_by: Optional[uuid.UUID]
    investigation_notes: Optional[str]
    resolution_description: Optional[str]
    corrective_action: Optional[str]
    preventive_measures: Optional[str]
    actual_cost: Optional[float]
    follow_up_required: bool
    follow_up_date: Optional[date]
    follow_up_notes: Optional[str]
    resolved_at: Optional[datetime]
    resolved_by: Optional[uuid.UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Computed fields
    age_days: int
    is_overdue: bool
    severity_weight: int
    requires_immediate_attention: bool


class IncidentSummary(BaseModel):
    """Incident summary for dashboard"""
    total_incidents: int
    open_incidents: int
    resolved_incidents: int
    critical_incidents: int
    overdue_incidents: int
    by_type: dict
    by_severity: dict
    average_resolution_time_days: Optional[float]
    total_cost: Optional[float]


class IncidentTrend(BaseModel):
    """Incident trend analysis"""
    month: str
    total_incidents: int
    by_type: dict
    by_severity: dict
    resolution_rate: float
    average_cost: Optional[float]