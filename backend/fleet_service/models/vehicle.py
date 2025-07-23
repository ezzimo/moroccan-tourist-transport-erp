"""
Vehicle model for fleet management
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
import uuid


class VehicleType(str, Enum):
    """Vehicle type enumeration"""
    BUS = "Bus"
    MINIBUS = "Minibus"
    SUV_4X4 = "SUV/4x4"
    SEDAN = "Sedan"
    VAN = "Van"
    MOTORCYCLE = "Motorcycle"


class VehicleStatus(str, Enum):
    """Vehicle status enumeration"""
    AVAILABLE = "Available"
    IN_USE = "In Use"
    MAINTENANCE = "Under Maintenance"
    OUT_OF_SERVICE = "Out of Service"
    RETIRED = "Retired"


class FuelType(str, Enum):
    """Fuel type enumeration"""
    GASOLINE = "Gasoline"
    DIESEL = "Diesel"
    HYBRID = "Hybrid"
    ELECTRIC = "Electric"
    LPG = "LPG"


class Vehicle(SQLModel, table=True):
    """Vehicle model for fleet management"""
    __tablename__ = "vehicles"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Basic Information
    license_plate: str = Field(unique=True, max_length=20, index=True)
    vehicle_type: VehicleType = Field(index=True)
    brand: str = Field(max_length=50)
    model: str = Field(max_length=50)
    year: int = Field(ge=1990, le=2030)
    color: Optional[str] = Field(default=None, max_length=30)
    
    # Capacity and Specifications
    seating_capacity: int = Field(ge=1, le=100)
    fuel_type: FuelType = Field(index=True)
    engine_size: Optional[float] = Field(default=None, ge=0)
    transmission: Optional[str] = Field(default=None, max_length=20)
    
    # Status and Tracking
    status: VehicleStatus = Field(default=VehicleStatus.AVAILABLE, index=True)
    current_odometer: int = Field(default=0, ge=0)
    
    # Compliance Dates
    registration_expiry: Optional[date] = Field(default=None, index=True)
    insurance_expiry: Optional[date] = Field(default=None, index=True)
    inspection_expiry: Optional[date] = Field(default=None, index=True)
    
    # Purchase Information
    purchase_date: Optional[date] = Field(default=None)
    purchase_price: Optional[float] = Field(default=None, ge=0)
    vin_number: Optional[str] = Field(default=None, max_length=50)
    
    # Additional Information
    notes: Optional[str] = Field(default=None, max_length=2000)
    is_active: bool = Field(default=True, index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    maintenance_records: List["MaintenanceRecord"] = Relationship(back_populates="vehicle")
    assignments: List["Assignment"] = Relationship(back_populates="vehicle")
    fuel_logs: List["FuelLog"] = Relationship(back_populates="vehicle")
    documents: List["Document"] = Relationship(back_populates="vehicle")
    
    def is_available_for_period(self, start_date: date, end_date: date) -> bool:
        """Check if vehicle is available for a specific period"""
        if self.status != VehicleStatus.AVAILABLE:
            return False
        
        # Check for overlapping assignments
        for assignment in self.assignments:
            if assignment.status == "Active" and assignment.overlaps_with(start_date, end_date):
                return False
        
        return True
    
    def get_compliance_status(self) -> dict:
        """Get compliance status for all required documents"""
        today = date.today()
        status = {}
        
        # Check registration
        if self.registration_expiry:
            days_until_expiry = (self.registration_expiry - today).days
            status["registration"] = {
                "expiry_date": self.registration_expiry,
                "days_until_expiry": days_until_expiry,
                "is_expired": days_until_expiry < 0,
                "needs_attention": days_until_expiry <= 30
            }
        
        # Check insurance
        if self.insurance_expiry:
            days_until_expiry = (self.insurance_expiry - today).days
            status["insurance"] = {
                "expiry_date": self.insurance_expiry,
                "days_until_expiry": days_until_expiry,
                "is_expired": days_until_expiry < 0,
                "needs_attention": days_until_expiry <= 30
            }
        
        # Check inspection
        if self.inspection_expiry:
            days_until_expiry = (self.inspection_expiry - today).days
            status["inspection"] = {
                "expiry_date": self.inspection_expiry,
                "days_until_expiry": days_until_expiry,
                "is_expired": days_until_expiry < 0,
                "needs_attention": days_until_expiry <= 30
            }
        
        return status
    
    def calculate_age_years(self) -> int:
        """Calculate vehicle age in years"""
        current_year = datetime.now().year
        return current_year - self.year
    
    def get_display_name(self) -> str:
        """Get display name for the vehicle"""
        return f"{self.brand} {self.model} ({self.license_plate})"