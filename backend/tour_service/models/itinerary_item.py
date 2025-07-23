"""
Itinerary item model for detailed tour schedule entries
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, time
from enum import Enum
import uuid


class ActivityType(str, Enum):
    """Activity type enumeration"""
    VISIT = "Visit"
    MEAL = "Meal"
    TRANSPORT = "Transport"
    ACCOMMODATION = "Accommodation"
    ACTIVITY = "Activity"
    FREE_TIME = "Free Time"
    MEETING_POINT = "Meeting Point"
    DEPARTURE = "Departure"
    ARRIVAL = "Arrival"
    BREAK = "Break"


class ItineraryItem(SQLModel, table=True):
    """Itinerary item model for detailed tour schedule entries"""
    __tablename__ = "itinerary_items"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Foreign Keys
    tour_instance_id: uuid.UUID = Field(foreign_key="tour_instances.id", index=True)
    
    # Schedule Information
    day_number: int = Field(ge=1, index=True)
    start_time: Optional[time] = Field(default=None)
    end_time: Optional[time] = Field(default=None)
    duration_minutes: Optional[int] = Field(default=None, ge=0)
    
    # Activity Details
    activity_type: ActivityType = Field(index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    
    # Location Information
    location_name: Optional[str] = Field(default=None, max_length=255)
    address: Optional[str] = Field(default=None, max_length=500)
    coordinates: Optional[str] = Field(default=None, max_length=100)  # lat,lng
    
    # Additional Information
    notes: Optional[str] = Field(default=None, max_length=1000)
    cost: Optional[float] = Field(default=None, ge=0)
    is_mandatory: bool = Field(default=True)
    
    # Execution Tracking
    is_completed: bool = Field(default=False)
    completed_at: Optional[datetime] = Field(default=None)
    completed_by: Optional[uuid.UUID] = Field(default=None)  # Staff member ID
    
    # Status
    is_cancelled: bool = Field(default=False)
    cancellation_reason: Optional[str] = Field(default=None, max_length=500)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    tour_instance: Optional["TourInstance"] = Relationship(back_populates="itinerary_items")
    
    def get_coordinates_tuple(self) -> Optional[tuple]:
        """Parse coordinates from string"""
        if not self.coordinates:
            return None
        try:
            lat, lng = self.coordinates.split(',')
            return (float(lat.strip()), float(lng.strip()))
        except:
            return None
    
    def set_coordinates_tuple(self, lat: float, lng: float):
        """Set coordinates as string"""
        self.coordinates = f"{lat},{lng}"
    
    def get_display_time(self) -> str:
        """Get formatted time display"""
        if self.start_time and self.end_time:
            return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
        elif self.start_time:
            return f"{self.start_time.strftime('%H:%M')}"
        else:
            return "Time TBD"