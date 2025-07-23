"""
Tour template-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from models.tour_template import TourCategory, DifficultyLevel
import uuid


class TourTemplateBase(BaseModel):
    title: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    category: TourCategory
    duration_days: int
    difficulty_level: DifficultyLevel = DifficultyLevel.EASY
    default_language: str = "French"
    default_region: str
    starting_location: Optional[str] = None
    ending_location: Optional[str] = None
    min_participants: int = 1
    max_participants: int = 20
    base_price: Optional[float] = None
    requirements: Optional[str] = None


class TourTemplateCreate(TourTemplateBase):
    highlights: Optional[List[str]] = []
    inclusions: Optional[List[str]] = []
    exclusions: Optional[List[str]] = []
    
    @validator('duration_days')
    def validate_duration(cls, v):
        if v < 1 or v > 30:
            raise ValueError('Duration must be between 1 and 30 days')
        return v
    
    @validator('min_participants', 'max_participants')
    def validate_participants(cls, v):
        if v < 1:
            raise ValueError('Participant count must be at least 1')
        return v


class TourTemplateUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    category: Optional[TourCategory] = None
    duration_days: Optional[int] = None
    difficulty_level: Optional[DifficultyLevel] = None
    default_language: Optional[str] = None
    default_region: Optional[str] = None
    starting_location: Optional[str] = None
    ending_location: Optional[str] = None
    min_participants: Optional[int] = None
    max_participants: Optional[int] = None
    base_price: Optional[float] = None
    highlights: Optional[List[str]] = None
    inclusions: Optional[List[str]] = None
    exclusions: Optional[List[str]] = None
    requirements: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class TourTemplateResponse(TourTemplateBase):
    id: uuid.UUID
    highlights: List[str] = []
    inclusions: List[str] = []
    exclusions: List[str] = []
    is_active: bool
    is_featured: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    @classmethod
    def from_model(cls, template):
        """Create response from database model"""
        return cls(
            id=template.id,
            title=template.title,
            description=template.description,
            short_description=template.short_description,
            category=template.category,
            duration_days=template.duration_days,
            difficulty_level=template.difficulty_level,
            default_language=template.default_language,
            default_region=template.default_region,
            starting_location=template.starting_location,
            ending_location=template.ending_location,
            min_participants=template.min_participants,
            max_participants=template.max_participants,
            base_price=template.base_price,
            highlights=template.get_highlights_list(),
            inclusions=template.get_inclusions_list(),
            exclusions=template.get_exclusions_list(),
            requirements=template.requirements,
            is_active=template.is_active,
            is_featured=template.is_featured,
            created_at=template.created_at,
            updated_at=template.updated_at
        )


class TourTemplateSearch(BaseModel):
    """Tour template search criteria"""
    query: Optional[str] = None
    category: Optional[TourCategory] = None
    difficulty_level: Optional[DifficultyLevel] = None
    region: Optional[str] = None
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    min_participants: Optional[int] = None
    max_participants: Optional[int] = None
    is_active: Optional[bool] = True
    is_featured: Optional[bool] = None