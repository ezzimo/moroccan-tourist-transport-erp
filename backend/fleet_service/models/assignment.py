"""
Assignment model for vehicle-tour allocation
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, date
from enum import Enum
import uuid


class AssignmentStatus(str, Enum):
    """Assignment status enumeration"""
    SCHEDULED = "Scheduled"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class Assignment(SQLModel, table=True):
    """Assignment model for linking vehicles to tour instances"""
    __tablename__ = "assignments"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Foreign Keys
    vehicle_id: uuid.UUID = Field(foreign_key="vehicles.id", index=True)
    tour_instance_id: uuid.UUID = Field(index=True)  # Reference to tour service
    driver_id: Optional[uuid.UUID] = Field(default=None, index=True)  # Reference to HR service
    
    # Assignment Details
    status: AssignmentStatus = Field(default=AssignmentStatus.SCHEDULED, index=True)
    start_date: date = Field(index=True)
    end_date: date = Field(index=True)
    
    # Odometer Readings
    start_odometer: Optional[int] = Field(default=None, ge=0)
    end_odometer: Optional[int] = Field(default=None, ge=0)
    
    # Assignment Information
    pickup_location: Optional[str] = Field(default=None, max_length=255)
    dropoff_location: Optional[str] = Field(default=None, max_length=255)
    estimated_distance: Optional[int] = Field(default=None, ge=0)  # in kilometers
    
    # Notes and Instructions
    notes: Optional[str] = Field(default=None, max_length=2000)
    special_instructions: Optional[str] = Field(default=None, max_length=1000)
    
    # Actual Execution
    actual_start_date: Optional[datetime] = Field(default=None)
    actual_end_date: Optional[datetime] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    assigned_by: Optional[uuid.UUID] = Field(default=None)
    
    # Relationships
    vehicle: Optional["Vehicle"] = Relationship(back_populates="assignments")
    
    def overlaps_with(self, start_date: date, end_date: date) -> bool:
        """Check if assignment overlaps with given date range"""
        return not (self.end_date < start_date or self.start_date > end_date)
    
    def get_duration_days(self) -> int:
        """Get assignment duration in days"""
        return (self.end_date - self.start_date).days + 1
    
    def get_distance_traveled(self) -> Optional[int]:
        """Calculate distance traveled during assignment"""
        if self.start_odometer and self.end_odometer:
            return self.end_odometer - self.start_odometer
        return None
    
    def is_active(self) -> bool:
        """Check if assignment is currently active"""
        today = date.today()
        return (
            self.status == AssignmentStatus.ACTIVE and
            self.start_date <= today <= self.end_date
        )