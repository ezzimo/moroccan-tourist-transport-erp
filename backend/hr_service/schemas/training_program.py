"""
Training program-related Pydantic schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from models.training_program import TrainingCategory, TrainingStatus, DeliveryMethod
import uuid


class TrainingProgramBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: TrainingCategory
    trainer_name: Optional[str] = None
    trainer_contact: Optional[str] = None
    delivery_method: DeliveryMethod = DeliveryMethod.IN_PERSON
    start_date: date
    end_date: date
    duration_hours: int
    location: Optional[str] = None
    max_participants: int = 20
    cost_per_participant: Optional[Decimal] = None
    total_budget: Optional[Decimal] = None
    is_mandatory: bool = False
    prerequisites: Optional[str] = None
    pass_score: float = 70.0


class TrainingProgramCreate(TrainingProgramBase):
    target_departments: Optional[List[str]] = []
    target_positions: Optional[List[str]] = []
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('duration_hours')
    def validate_duration(cls, v):
        if v < 1:
            raise ValueError('Duration must be at least 1 hour')
        if v > 1000:
            raise ValueError('Duration seems unrealistic')
        return v
    
    @validator('max_participants')
    def validate_max_participants(cls, v):
        if v < 1:
            raise ValueError('Maximum participants must be at least 1')
        if v > 1000:
            raise ValueError('Maximum participants seems unrealistic')
        return v
    
    @validator('pass_score')
    def validate_pass_score(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Pass score must be between 0 and 100')
        return v


class TrainingProgramUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[TrainingCategory] = None
    trainer_name: Optional[str] = None
    trainer_contact: Optional[str] = None
    delivery_method: Optional[DeliveryMethod] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    duration_hours: Optional[int] = None
    location: Optional[str] = None
    max_participants: Optional[int] = None
    cost_per_participant: Optional[Decimal] = None
    total_budget: Optional[Decimal] = None
    is_mandatory: Optional[bool] = None
    prerequisites: Optional[str] = None
    target_departments: Optional[List[str]] = None
    target_positions: Optional[List[str]] = None
    pass_score: Optional[float] = None
    status: Optional[TrainingStatus] = None
    is_active: Optional[bool] = None


class TrainingProgramResponse(TrainingProgramBase):
    id: uuid.UUID
    target_departments: List[str] = []
    target_positions: List[str] = []
    status: TrainingStatus
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    duration_days: int
    cost_per_hour: Optional[Decimal]
    is_upcoming: bool
    is_ongoing: bool


class TrainingProgramSummary(TrainingProgramResponse):
    """Extended training program response with summary statistics"""
    enrolled_count: int = 0
    completed_count: int = 0
    passed_count: int = 0
    average_score: Optional[float] = None
    completion_rate: float = 0.0
    pass_rate: float = 0.0
    total_cost: Optional[Decimal] = None
    average_rating: Optional[float] = None


class TrainingSearch(BaseModel):
    """Training program search criteria"""
    query: Optional[str] = None
    category: Optional[TrainingCategory] = None
    delivery_method: Optional[DeliveryMethod] = None
    status: Optional[TrainingStatus] = None
    trainer_name: Optional[str] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    is_mandatory: Optional[bool] = None
    is_active: Optional[bool] = True


class TrainingStats(BaseModel):
    """Training statistics"""
    total_programs: int
    active_programs: int
    completed_programs: int
    total_participants: int
    by_category: Dict[str, int]
    by_delivery_method: Dict[str, int]
    completion_rates: Dict[str, float]
    average_scores: Dict[str, float]
    total_training_hours: int
    total_cost: Optional[Decimal]
    monthly_trends: Dict[str, int]