"""
Driver assignment-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime, date
from models.driver_assignment import AssignmentStatus
import uuid


class DriverAssignmentBase(BaseModel):
    tour_instance_id: uuid.UUID
    vehicle_id: Optional[uuid.UUID] = None
    start_date: date
    end_date: date
    tour_title: Optional[str] = None
    pickup_location: Optional[str] = None
    dropoff_location: Optional[str] = None
    estimated_duration_hours: Optional[int] = None
    special_instructions: Optional[str] = None


class DriverAssignmentCreate(DriverAssignmentBase):
    driver_id: uuid.UUID
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class DriverAssignmentUpdate(BaseModel):
    vehicle_id: Optional[uuid.UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[AssignmentStatus] = None
    tour_title: Optional[str] = None
    pickup_location: Optional[str] = None
    dropoff_location: Optional[str] = None
    estimated_duration_hours: Optional[int] = None
    special_instructions: Optional[str] = None
    customer_rating: Optional[float] = None
    customer_feedback: Optional[str] = None
    notes: Optional[str] = None


class DriverAssignmentResponse(DriverAssignmentBase):
    id: uuid.UUID
    driver_id: uuid.UUID
    status: AssignmentStatus
    assigned_by: uuid.UUID
    assigned_at: datetime
    confirmed_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    actual_start_time: Optional[datetime]
    actual_end_time: Optional[datetime]
    customer_rating: Optional[float]
    customer_feedback: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Computed fields
    duration_days: int
    is_active: bool
    is_overdue: bool
    actual_duration_hours: Optional[float]
    is_on_time: Optional[bool]


class AssignmentSummary(BaseModel):
    """Assignment summary for dashboard"""
    total_assignments: int
    active_assignments: int
    completed_assignments: int
    cancelled_assignments: int
    overdue_assignments: int
    average_rating: Optional[float]
    completion_rate: float
    on_time_rate: float


class AssignmentConflict(BaseModel):
    """Assignment conflict information"""
    conflicting_assignment_id: uuid.UUID
    conflict_start_date: date
    conflict_end_date: date
    conflict_description: str