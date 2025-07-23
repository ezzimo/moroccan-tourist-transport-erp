"""
Vehicle-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from models.vehicle import VehicleType, VehicleStatus, FuelType
import uuid


class VehicleBase(BaseModel):
    license_plate: str
    vehicle_type: VehicleType
    brand: str
    model: str
    year: int
    color: Optional[str] = None
    seating_capacity: int
    fuel_type: FuelType
    engine_size: Optional[float] = None
    transmission: Optional[str] = None


class VehicleCreate(VehicleBase):
    current_odometer: int = 0
    registration_expiry: Optional[date] = None
    insurance_expiry: Optional[date] = None
    inspection_expiry: Optional[date] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    vin_number: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('year')
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v < 1990 or v > current_year + 1:
            raise ValueError(f'Year must be between 1990 and {current_year + 1}')
        return v
    
    @validator('seating_capacity')
    def validate_seating_capacity(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Seating capacity must be between 1 and 100')
        return v


class VehicleUpdate(BaseModel):
    license_plate: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    seating_capacity: Optional[int] = None
    fuel_type: Optional[FuelType] = None
    engine_size: Optional[float] = None
    transmission: Optional[str] = None
    status: Optional[VehicleStatus] = None
    current_odometer: Optional[int] = None
    registration_expiry: Optional[date] = None
    insurance_expiry: Optional[date] = None
    inspection_expiry: Optional[date] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    vin_number: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class VehicleResponse(VehicleBase):
    id: uuid.UUID
    status: VehicleStatus
    current_odometer: int
    registration_expiry: Optional[date]
    insurance_expiry: Optional[date]
    inspection_expiry: Optional[date]
    purchase_date: Optional[date]
    purchase_price: Optional[float]
    vin_number: Optional[str]
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    display_name: str
    age_years: int
    compliance_status: Dict[str, Any]


class VehicleSummary(VehicleResponse):
    """Extended vehicle response with summary statistics"""
    total_assignments: int = 0
    active_assignments: int = 0
    total_maintenance_records: int = 0
    last_maintenance_date: Optional[date] = None
    total_maintenance_cost: float = 0.0
    average_fuel_efficiency: Optional[float] = None
    total_distance_traveled: int = 0
    days_since_last_service: Optional[int] = None
    upcoming_maintenance: List[Dict[str, Any]] = []
    compliance_alerts: List[Dict[str, Any]] = []


class VehicleSearch(BaseModel):
    """Vehicle search criteria"""
    query: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    status: Optional[VehicleStatus] = None
    fuel_type: Optional[FuelType] = None
    brand: Optional[str] = None
    min_seating_capacity: Optional[int] = None
    max_seating_capacity: Optional[int] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    is_active: Optional[bool] = True
    available_from: Optional[date] = None
    available_to: Optional[date] = None


class VehicleAvailability(BaseModel):
    """Vehicle availability check"""
    vehicle_id: uuid.UUID
    start_date: date
    end_date: date
    is_available: bool
    conflicting_assignments: List[uuid.UUID] = []
    status: VehicleStatus
    notes: Optional[str] = None