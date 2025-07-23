"""
Assignment-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime, date
from models.assignment import AssignmentStatus
import uuid


class AssignmentBase(BaseModel):
    vehicle_id: uuid.UUID
    tour_instance_id: uuid.UUID
    driver_id: Optional[uuid.UUID] = None
    start_date: date
    end_date: date
    pickup_location: Optional[str] = None
    dropoff_location: Optional[str] = None
    estimated_distance: Optional[int] = None
    notes: Optional[str] = None
    special_instructions: Optional[str] = None


class AssignmentCreate(AssignmentBase):
    assigned_by: Optional[uuid.UUID] = None
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('estimated_distance')
    def validate_distance(cls, v):
        if v is not None and v < 0:
            raise ValueError('Estimated distance must be non-negative')
        return v


class AssignmentUpdate(BaseModel):
    driver_id: Optional[uuid.UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[AssignmentStatus] = None
    start_odometer: Optional[int] = None
    end_odometer: Optional[int] = None
    pickup_location: Optional[str] = None
    dropoff_location: Optional[str] = None
    estimated_distance: Optional[int] = None
    notes: Optional[str] = None
    special_instructions: Optional[str] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None


class AssignmentResponse(AssignmentBase):
    id: uuid.UUID
    status: AssignmentStatus
    start_odometer: Optional[int]
    end_odometer: Optional[int]
    actual_start_date: Optional[datetime]
    actual_end_date: Optional[datetime]
    assigned_by: Optional[uuid.UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    duration_days: int
    distance_traveled: Optional[int]
    is_active: bool


class AssignmentConflict(BaseModel):
    """Assignment conflict information"""
    vehicle_id: uuid.UUID
    conflicting_assignment_id: uuid.UUID
    conflict_start: date
    conflict_end: date
    message: str