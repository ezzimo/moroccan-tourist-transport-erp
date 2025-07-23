"""
Itinerary item-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, Tuple
from datetime import datetime, time
from models.itinerary_item import ActivityType
import uuid


class ItineraryItemBase(BaseModel):
    day_number: int
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration_minutes: Optional[int] = None
    activity_type: ActivityType
    title: str
    description: Optional[str] = None
    location_name: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    cost: Optional[float] = None
    is_mandatory: bool = True


class ItineraryItemCreate(ItineraryItemBase):
    tour_instance_id: uuid.UUID
    coordinates: Optional[Tuple[float, float]] = None
    
    @validator('day_number')
    def validate_day_number(cls, v):
        if v < 1:
            raise ValueError('Day number must be at least 1')
        return v
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        if v and 'start_time' in values and values['start_time'] and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v
    
    @validator('duration_minutes')
    def validate_duration(cls, v):
        if v is not None and v < 0:
            raise ValueError('Duration must be non-negative')
        return v


class ItineraryItemUpdate(BaseModel):
    day_number: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration_minutes: Optional[int] = None
    activity_type: Optional[ActivityType] = None
    title: Optional[str] = None
    description: Optional[str] = None
    location_name: Optional[str] = None
    address: Optional[str] = None
    coordinates: Optional[Tuple[float, float]] = None
    notes: Optional[str] = None
    cost: Optional[float] = None
    is_mandatory: Optional[bool] = None
    is_cancelled: Optional[bool] = None
    cancellation_reason: Optional[str] = None


class ItineraryItemResponse(ItineraryItemBase):
    id: uuid.UUID
    tour_instance_id: uuid.UUID
    coordinates: Optional[Tuple[float, float]] = None
    is_completed: bool
    completed_at: Optional[datetime]
    completed_by: Optional[uuid.UUID]
    is_cancelled: bool
    cancellation_reason: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    display_time: str
    
    @classmethod
    def from_model(cls, item):
        """Create response from database model"""
        return cls(
            id=item.id,
            tour_instance_id=item.tour_instance_id,
            day_number=item.day_number,
            start_time=item.start_time,
            end_time=item.end_time,
            duration_minutes=item.duration_minutes,
            activity_type=item.activity_type,
            title=item.title,
            description=item.description,
            location_name=item.location_name,
            address=item.address,
            coordinates=item.get_coordinates_tuple(),
            notes=item.notes,
            cost=item.cost,
            is_mandatory=item.is_mandatory,
            is_completed=item.is_completed,
            completed_at=item.completed_at,
            completed_by=item.completed_by,
            is_cancelled=item.is_cancelled,
            cancellation_reason=item.cancellation_reason,
            created_at=item.created_at,
            updated_at=item.updated_at,
            display_time=item.get_display_time()
        )


class ItineraryItemCompletion(BaseModel):
    """Schema for marking itinerary items as completed"""
    notes: Optional[str] = None
    actual_duration_minutes: Optional[int] = None


class ItineraryDayResponse(BaseModel):
    """Schema for daily itinerary view"""
    day_number: int
    date: Optional[str] = None
    items: list[ItineraryItemResponse] = []
    total_items: int = 0
    completed_items: int = 0
    estimated_duration_minutes: int = 0