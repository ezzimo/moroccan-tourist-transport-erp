"""
Non-conformity-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime, date
from models.nonconformity import Severity, NCStatus
import uuid


class NonConformityBase(BaseModel):
    title: str
    description: str
    severity: Severity
    root_cause: Optional[str] = None
    contributing_factors: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    assigned_to: Optional[uuid.UUID] = None
    due_date: Optional[date] = None
    target_completion_date: Optional[date] = None
    estimated_cost: Optional[float] = None


class NonConformityCreate(NonConformityBase):
    audit_id: uuid.UUID
    
    @validator('due_date')
    def validate_due_date(cls, v):
        if v and v < date.today():
            raise ValueError('Due date cannot be in the past')
        return v
    
    @validator('estimated_cost')
    def validate_cost(cls, v):
        if v is not None and v < 0:
            raise ValueError('Estimated cost cannot be negative')
        return v


class NonConformityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[Severity] = None
    root_cause: Optional[str] = None
    contributing_factors: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    assigned_to: Optional[uuid.UUID] = None
    due_date: Optional[date] = None
    target_completion_date: Optional[date] = None
    actual_completion_date: Optional[date] = None
    status: Optional[NCStatus] = None
    progress_notes: Optional[str] = None
    verified_by: Optional[uuid.UUID] = None
    verification_date: Optional[date] = None
    verification_notes: Optional[str] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    is_recurring: Optional[bool] = None
    previous_nc_id: Optional[uuid.UUID] = None


class NonConformityResponse(NonConformityBase):
    id: uuid.UUID
    audit_id: uuid.UUID
    nc_number: str
    status: NCStatus
    actual_completion_date: Optional[date]
    progress_notes: Optional[str]
    verified_by: Optional[uuid.UUID]
    verification_date: Optional[date]
    verification_notes: Optional[str]
    actual_cost: Optional[float]
    is_recurring: bool
    previous_nc_id: Optional[uuid.UUID]
    identified_date: date
    created_at: datetime
    updated_at: Optional[datetime]
    is_overdue: bool
    days_overdue: int
    age_days: int
    is_critical_overdue: bool
    resolution_time_days: Optional[int]


class NonConformityResolution(BaseModel):
    """Schema for resolving non-conformity"""
    corrective_action: str
    preventive_action: Optional[str] = None
    actual_completion_date: date
    actual_cost: Optional[float] = None
    resolution_notes: Optional[str] = None
    
    @validator('actual_completion_date')
    def validate_completion_date(cls, v):
        if v > date.today():
            raise ValueError('Completion date cannot be in the future')
        return v


class NonConformityVerification(BaseModel):
    """Schema for verifying non-conformity resolution"""
    verification_notes: str
    verified: bool
    follow_up_required: bool = False
    follow_up_notes: Optional[str] = None


class NonConformitySummary(BaseModel):
    """Non-conformity summary for dashboard"""
    total_nonconformities: int
    by_severity: Dict[str, int]
    by_status: Dict[str, int]
    overdue_count: int
    critical_overdue_count: int
    average_resolution_time_days: Optional[float]
    recurring_issues: int