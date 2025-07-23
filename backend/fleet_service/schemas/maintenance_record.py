"""
Maintenance record-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime, date
from models.maintenance_record import MaintenanceType
import uuid


class MaintenanceRecordBase(BaseModel):
    maintenance_type: MaintenanceType
    description: str
    date_performed: date
    provider_name: Optional[str] = None
    provider_contact: Optional[str] = None
    cost: Optional[float] = None
    currency: str = "MAD"
    odometer_reading: Optional[int] = None
    parts_replaced: Optional[str] = None
    labor_hours: Optional[float] = None
    next_service_date: Optional[date] = None
    next_service_odometer: Optional[int] = None
    warranty_until: Optional[date] = None
    notes: Optional[str] = None


class MaintenanceRecordCreate(MaintenanceRecordBase):
    vehicle_id: uuid.UUID
    performed_by: Optional[uuid.UUID] = None
    approved_by: Optional[uuid.UUID] = None
    
    @validator('cost')
    def validate_cost(cls, v):
        if v is not None and v < 0:
            raise ValueError('Cost must be non-negative')
        return v
    
    @validator('labor_hours')
    def validate_labor_hours(cls, v):
        if v is not None and v < 0:
            raise ValueError('Labor hours must be non-negative')
        return v
    
    @validator('next_service_date')
    def validate_next_service_date(cls, v, values):
        if v and 'date_performed' in values and v <= values['date_performed']:
            raise ValueError('Next service date must be after the performed date')
        return v


class MaintenanceRecordUpdate(BaseModel):
    maintenance_type: Optional[MaintenanceType] = None
    description: Optional[str] = None
    date_performed: Optional[date] = None
    provider_name: Optional[str] = None
    provider_contact: Optional[str] = None
    cost: Optional[float] = None
    currency: Optional[str] = None
    odometer_reading: Optional[int] = None
    parts_replaced: Optional[str] = None
    labor_hours: Optional[float] = None
    next_service_date: Optional[date] = None
    next_service_odometer: Optional[int] = None
    is_completed: Optional[bool] = None
    warranty_until: Optional[date] = None
    notes: Optional[str] = None
    performed_by: Optional[uuid.UUID] = None
    approved_by: Optional[uuid.UUID] = None


class MaintenanceRecordResponse(MaintenanceRecordBase):
    id: uuid.UUID
    vehicle_id: uuid.UUID
    is_completed: bool
    performed_by: Optional[uuid.UUID]
    approved_by: Optional[uuid.UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    is_under_warranty: bool
    cost_per_hour: Optional[float]


class MaintenanceStats(BaseModel):
    """Maintenance statistics"""
    total_records: int
    total_cost: float
    by_type: dict
    by_month: dict
    average_cost: float
    preventive_percentage: float
    vehicles_needing_service: int