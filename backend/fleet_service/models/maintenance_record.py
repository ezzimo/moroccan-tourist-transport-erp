"""
Maintenance record model for vehicle service tracking
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, date
from enum import Enum
import uuid


class MaintenanceType(str, Enum):
    """Maintenance type enumeration"""
    PREVENTIVE = "Preventive"
    CORRECTIVE = "Corrective"
    EMERGENCY = "Emergency"
    INSPECTION = "Inspection"
    RECALL = "Recall"


class MaintenanceRecord(SQLModel, table=True):
    """Maintenance record model for tracking vehicle service history"""
    __tablename__ = "maintenance_records"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Foreign Keys
    vehicle_id: uuid.UUID = Field(foreign_key="vehicles.id", index=True)
    
    # Maintenance Details
    maintenance_type: MaintenanceType = Field(index=True)
    description: str = Field(max_length=2000)
    date_performed: date = Field(index=True)
    
    # Service Provider
    provider_name: Optional[str] = Field(default=None, max_length=255)
    provider_contact: Optional[str] = Field(default=None, max_length=100)
    
    # Cost and Mileage
    cost: Optional[float] = Field(default=None, ge=0)
    currency: str = Field(default="MAD", max_length=3)
    odometer_reading: Optional[int] = Field(default=None, ge=0)
    
    # Parts and Labor
    parts_replaced: Optional[str] = Field(default=None, max_length=1000)
    labor_hours: Optional[float] = Field(default=None, ge=0)
    
    # Next Service
    next_service_date: Optional[date] = Field(default=None)
    next_service_odometer: Optional[int] = Field(default=None, ge=0)
    
    # Status and Notes
    is_completed: bool = Field(default=True)
    warranty_until: Optional[date] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=1000)
    
    # Staff Information
    performed_by: Optional[uuid.UUID] = Field(default=None, index=True)
    approved_by: Optional[uuid.UUID] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    vehicle: Optional["Vehicle"] = Relationship(back_populates="maintenance_records")
    
    def is_under_warranty(self) -> bool:
        """Check if maintenance is still under warranty"""
        if not self.warranty_until:
            return False
        return date.today() <= self.warranty_until
    
    def get_cost_per_hour(self) -> Optional[float]:
        """Calculate cost per labor hour"""
        if self.cost and self.labor_hours and self.labor_hours > 0:
            return self.cost / self.labor_hours
        return None