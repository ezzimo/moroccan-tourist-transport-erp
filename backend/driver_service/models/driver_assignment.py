"""
Driver assignment model for tour assignments
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, date
from enum import Enum
import uuid


class AssignmentStatus(str, Enum):
    """Assignment status enumeration"""
    ASSIGNED = "Assigned"
    CONFIRMED = "Confirmed"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    NO_SHOW = "No Show"


class DriverAssignment(SQLModel, table=True):
    """Driver assignment model for linking drivers to tours"""
    __tablename__ = "driver_assignments"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Foreign Keys
    driver_id: uuid.UUID = Field(foreign_key="drivers.id", index=True)
    tour_instance_id: uuid.UUID = Field(index=True)  # Reference to tour service
    vehicle_id: Optional[uuid.UUID] = Field(default=None, index=True)  # Reference to fleet service
    
    # Assignment Details
    status: AssignmentStatus = Field(default=AssignmentStatus.ASSIGNED, index=True)
    start_date: date = Field(index=True)
    end_date: date = Field(index=True)
    
    # Tour Information (cached for performance)
    tour_title: Optional[str] = Field(default=None, max_length=255)
    pickup_location: Optional[str] = Field(default=None, max_length=255)
    dropoff_location: Optional[str] = Field(default=None, max_length=255)
    estimated_duration_hours: Optional[int] = Field(default=None, ge=0)
    
    # Assignment Metadata
    assigned_by: uuid.UUID = Field(index=True)  # User who made the assignment
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = Field(default=None)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    
    # Performance Tracking
    actual_start_time: Optional[datetime] = Field(default=None)
    actual_end_time: Optional[datetime] = Field(default=None)
    customer_rating: Optional[float] = Field(default=None, ge=0, le=5)
    customer_feedback: Optional[str] = Field(default=None, max_length=1000)
    
    # Additional Information
    special_instructions: Optional[str] = Field(default=None, max_length=1000)
    notes: Optional[str] = Field(default=None, max_length=1000)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    driver: Optional["Driver"] = Relationship(back_populates="assignments")
    
    def get_duration_days(self) -> int:
        """Get assignment duration in days"""
        return (self.end_date - self.start_date).days + 1
    
    def is_active(self) -> bool:
        """Check if assignment is currently active"""
        today = date.today()
        return (
            self.status in [AssignmentStatus.ASSIGNED, AssignmentStatus.CONFIRMED, AssignmentStatus.IN_PROGRESS] and
            self.start_date <= today <= self.end_date
        )
    
    def is_overdue(self) -> bool:
        """Check if assignment is overdue"""
        return (
            self.status == AssignmentStatus.ASSIGNED and
            date.today() > self.end_date
        )
    
    def calculate_actual_duration_hours(self) -> Optional[float]:
        """Calculate actual duration in hours"""
        if not self.actual_start_time or not self.actual_end_time:
            return None
        
        duration = self.actual_end_time - self.actual_start_time
        return duration.total_seconds() / 3600
    
    def is_on_time(self) -> Optional[bool]:
        """Check if assignment was completed on time"""
        if not self.actual_start_time or not self.completed_at:
            return None
        
        # Consider on-time if started within 30 minutes of scheduled time
        scheduled_start = datetime.combine(self.start_date, datetime.min.time())
        time_diff = abs((self.actual_start_time - scheduled_start).total_seconds() / 60)
        
        return time_diff <= 30  # 30 minutes tolerance