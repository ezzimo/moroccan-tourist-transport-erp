"""
Fuel log model for tracking fuel consumption
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, date
from enum import Enum
import uuid


class FuelLog(SQLModel, table=True):
    """Fuel log model for tracking vehicle fuel consumption"""
    __tablename__ = "fuel_logs"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Foreign Keys
    vehicle_id: uuid.UUID = Field(foreign_key="vehicles.id", index=True)
    
    # Fuel Details
    date: date = Field(index=True)
    odometer_reading: int = Field(ge=0)
    fuel_amount: float = Field(ge=0)  # in liters
    fuel_cost: float = Field(ge=0)  # total cost
    price_per_liter: float = Field(ge=0)
    
    # Location and Provider
    station_name: Optional[str] = Field(default=None, max_length=255)
    location: Optional[str] = Field(default=None, max_length=255)
    
    # Trip Information
    trip_purpose: Optional[str] = Field(default=None, max_length=100)
    driver_id: Optional[uuid.UUID] = Field(default=None, index=True)
    
    # Efficiency Calculations
    distance_since_last_fill: Optional[int] = Field(default=None, ge=0)
    fuel_efficiency: Optional[float] = Field(default=None, ge=0)  # km per liter
    
    # Additional Information
    is_full_tank: bool = Field(default=True)
    receipt_number: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = Field(default=None, max_length=500)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[uuid.UUID] = Field(default=None)
    
    # Relationships
    vehicle: Optional["Vehicle"] = Relationship(back_populates="fuel_logs")
    
    def calculate_cost_per_km(self) -> Optional[float]:
        """Calculate fuel cost per kilometer"""
        if self.distance_since_last_fill and self.distance_since_last_fill > 0:
            return self.fuel_cost / self.distance_since_last_fill
        return None