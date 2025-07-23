"""
Tour instance model for operationalized tours
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
import uuid


class TourStatus(str, Enum):
    """Tour instance status enumeration"""
    PLANNED = "Planned"
    CONFIRMED = "Confirmed"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    POSTPONED = "Postponed"


class TourInstance(SQLModel, table=True):
    """Tour instance model for operationalized tours linked to bookings"""
    __tablename__ = "tour_instances"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Foreign Keys
    template_id: uuid.UUID = Field(foreign_key="tour_templates.id", index=True)
    booking_id: uuid.UUID = Field(index=True)  # Reference to booking service
    customer_id: uuid.UUID = Field(index=True)  # Reference to CRM service
    
    # Tour Details
    status: TourStatus = Field(default=TourStatus.PLANNED, index=True)
    title: str = Field(max_length=255)  # Can be customized from template
    
    # Dates and Duration
    start_date: date = Field(index=True)
    end_date: date = Field(index=True)
    actual_start_date: Optional[datetime] = Field(default=None)
    actual_end_date: Optional[datetime] = Field(default=None)
    
    # Participants
    participant_count: int = Field(ge=1)
    lead_participant_name: str = Field(max_length=255)
    participant_details: Optional[str] = Field(default=None)  # JSON string
    
    # Resource Assignment
    assigned_guide_id: Optional[uuid.UUID] = Field(default=None, index=True)
    assigned_vehicle_id: Optional[uuid.UUID] = Field(default=None, index=True)
    assigned_driver_id: Optional[uuid.UUID] = Field(default=None, index=True)
    
    # Tour Configuration
    language: str = Field(default="French", max_length=50)
    special_requirements: Optional[str] = Field(default=None, max_length=2000)
    internal_notes: Optional[str] = Field(default=None, max_length=2000)
    
    # Progress Tracking
    current_day: int = Field(default=1, ge=1)
    completion_percentage: float = Field(default=0.0, ge=0, le=100)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    confirmed_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    template: Optional["TourTemplate"] = Relationship(back_populates="tour_instances")
    itinerary_items: List["ItineraryItem"] = Relationship(back_populates="tour_instance")
    incidents: List["Incident"] = Relationship(back_populates="tour_instance")
    
    def get_participant_details_dict(self) -> dict:
        """Parse participant details from JSON string"""
        if not self.participant_details:
            return {}
        try:
            import json
            return json.loads(self.participant_details)
        except:
            return {}
    
    def set_participant_details_dict(self, details: dict):
        """Set participant details as JSON string"""
        import json
        self.participant_details = json.dumps(details) if details else None
    
    def get_duration_days(self) -> int:
        """Get tour duration in days"""
        return (self.end_date - self.start_date).days + 1
    
    def is_active(self) -> bool:
        """Check if tour is currently active"""
        return self.status in [TourStatus.CONFIRMED, TourStatus.IN_PROGRESS]
    
    def can_be_modified(self) -> bool:
        """Check if tour can be modified"""
        return self.status in [TourStatus.PLANNED, TourStatus.CONFIRMED]