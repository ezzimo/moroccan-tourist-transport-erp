"""
Tour instance-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime, date
from models.tour_instance import TourStatus
import uuid


class TourInstanceBase(BaseModel):
    template_id: uuid.UUID
    booking_id: uuid.UUID
    customer_id: uuid.UUID
    title: str
    start_date: date
    end_date: date
    participant_count: int
    lead_participant_name: str
    language: str = "French"
    special_requirements: Optional[str] = None


class TourInstanceCreate(TourInstanceBase):
    participant_details: Optional[Dict[str, Any]] = None
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('participant_count')
    def validate_participant_count(cls, v):
        if v < 1:
            raise ValueError('Participant count must be at least 1')
        return v


class TourInstanceUpdate(BaseModel):
    title: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    participant_count: Optional[int] = None
    lead_participant_name: Optional[str] = None
    language: Optional[str] = None
    special_requirements: Optional[str] = None
    participant_details: Optional[Dict[str, Any]] = None
    internal_notes: Optional[str] = None
    current_day: Optional[int] = None
    completion_percentage: Optional[float] = None


class TourInstanceResponse(TourInstanceBase):
    id: uuid.UUID
    status: TourStatus
    actual_start_date: Optional[datetime]
    actual_end_date: Optional[datetime]
    assigned_guide_id: Optional[uuid.UUID]
    assigned_vehicle_id: Optional[uuid.UUID]
    assigned_driver_id: Optional[uuid.UUID]
    participant_details: Dict[str, Any] = {}
    internal_notes: Optional[str]
    current_day: int
    completion_percentage: float
    created_at: datetime
    updated_at: Optional[datetime]
    confirmed_at: Optional[datetime]
    
    @classmethod
    def from_model(cls, instance):
        """Create response from database model"""
        return cls(
            id=instance.id,
            template_id=instance.template_id,
            booking_id=instance.booking_id,
            customer_id=instance.customer_id,
            title=instance.title,
            status=instance.status,
            start_date=instance.start_date,
            end_date=instance.end_date,
            actual_start_date=instance.actual_start_date,
            actual_end_date=instance.actual_end_date,
            participant_count=instance.participant_count,
            lead_participant_name=instance.lead_participant_name,
            assigned_guide_id=instance.assigned_guide_id,
            assigned_vehicle_id=instance.assigned_vehicle_id,
            assigned_driver_id=instance.assigned_driver_id,
            language=instance.language,
            special_requirements=instance.special_requirements,
            participant_details=instance.get_participant_details_dict(),
            internal_notes=instance.internal_notes,
            current_day=instance.current_day,
            completion_percentage=instance.completion_percentage,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
            confirmed_at=instance.confirmed_at
        )


class TourInstanceSummary(TourInstanceResponse):
    """Extended tour instance response with summary information"""
    duration_days: int = 1
    itinerary_items_count: int = 0
    completed_items_count: int = 0
    incidents_count: int = 0
    unresolved_incidents_count: int = 0
    is_active: bool = False
    can_be_modified: bool = True
    template_title: Optional[str] = None
    customer_name: Optional[str] = None


class TourAssignment(BaseModel):
    """Schema for tour resource assignment"""
    guide_id: Optional[uuid.UUID] = None
    vehicle_id: Optional[uuid.UUID] = None
    driver_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class TourStatusUpdate(BaseModel):
    """Schema for tour status updates"""
    status: TourStatus
    notes: Optional[str] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None


class TourProgressUpdate(BaseModel):
    """Schema for tour progress updates"""
    current_day: int
    completion_percentage: float
    notes: Optional[str] = None


class TourInstanceSearch(BaseModel):
    """Tour instance search criteria"""
    template_id: Optional[uuid.UUID] = None
    booking_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    status: Optional[TourStatus] = None
    assigned_guide_id: Optional[uuid.UUID] = None
    assigned_vehicle_id: Optional[uuid.UUID] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    region: Optional[str] = None