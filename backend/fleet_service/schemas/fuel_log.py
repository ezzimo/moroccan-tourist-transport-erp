"""
Fuel log-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime, date
import uuid


class FuelLogBase(BaseModel):
    slot_date: date
    odometer_reading: int
    fuel_amount: float
    fuel_cost: float
    price_per_liter: float
    station_name: Optional[str] = None
    location: Optional[str] = None
    trip_purpose: Optional[str] = None
    driver_id: Optional[uuid.UUID] = None
    is_full_tank: bool = True
    receipt_number: Optional[str] = None
    notes: Optional[str] = None


class FuelLogCreate(FuelLogBase):
    vehicle_id: uuid.UUID
    created_by: Optional[uuid.UUID] = None
    
    @validator('fuel_amount', 'fuel_cost', 'price_per_liter')
    def validate_positive_values(cls, v):
        if v < 0:
            raise ValueError('Value must be non-negative')
        return v
    
    @validator('odometer_reading')
    def validate_odometer(cls, v):
        if v < 0:
            raise ValueError('Odometer reading must be non-negative')
        return v


class FuelLogUpdate(BaseModel):
    slot_date: Optional[date] = None
    odometer_reading: Optional[int] = None
    fuel_amount: Optional[float] = None
    fuel_cost: Optional[float] = None
    price_per_liter: Optional[float] = None
    station_name: Optional[str] = None
    location: Optional[str] = None
    trip_purpose: Optional[str] = None
    driver_id: Optional[uuid.UUID] = None
    is_full_tank: Optional[bool] = None
    receipt_number: Optional[str] = None
    notes: Optional[str] = None


class FuelLogResponse(FuelLogBase):
    id: uuid.UUID
    vehicle_id: uuid.UUID
    distance_since_last_fill: Optional[int]
    fuel_efficiency: Optional[float]
    created_at: datetime
    created_by: Optional[uuid.UUID]
    cost_per_km: Optional[float]


class FuelStats(BaseModel):
    """Fuel consumption statistics"""
    total_fuel_consumed: float
    total_fuel_cost: float
    average_price_per_liter: float
    average_fuel_efficiency: Optional[float]
    total_distance: int
    cost_per_km: Optional[float]
    by_month: dict
    by_vehicle_type: dict