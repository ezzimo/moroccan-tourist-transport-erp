"""
Job application-related Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from models.job_application import ApplicationSource, ApplicationStage, Priority
import uuid


class JobApplicationBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    national_id: Optional[str] = None
    position_applied: str
    department: str
    source: ApplicationSource
    years_of_experience: Optional[int] = None
    education_level: Optional[str] = None
    expected_salary: Optional[float] = None


class JobApplicationCreate(JobApplicationBase):
    languages: Optional[List[str]] = []
    skills: Optional[List[str]] = []
    
    @validator('years_of_experience')
    def validate_experience(cls, v):
        if v is not None and v < 0:
            raise ValueError('Years of experience cannot be negative')
        if v is not None and v > 50:
            raise ValueError('Years of experience seems unrealistic')
        return v
    
    @validator('expected_salary')
    def validate_salary(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Expected salary must be greater than 0')
        return v


class JobApplicationUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    position_applied: Optional[str] = None
    department: Optional[str] = None
    stage: Optional[ApplicationStage] = None
    priority: Optional[Priority] = None
    years_of_experience: Optional[int] = None
    education_level: Optional[str] = None
    languages: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    expected_salary: Optional[float] = None
    assigned_recruiter_id: Optional[uuid.UUID] = None
    interview_date: Optional[datetime] = None
    interview_location: Optional[str] = None
    screening_score: Optional[float] = None
    interview_score: Optional[float] = None
    technical_score: Optional[float] = None
    overall_rating: Optional[float] = None
    recruiter_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    is_active: Optional[bool] = None


class JobApplicationResponse(JobApplicationBase):
    id: uuid.UUID
    stage: ApplicationStage
    priority: Priority
    languages: List[str] = []
    skills: List[str] = []
    assigned_recruiter_id: Optional[uuid.UUID]
    interview_date: Optional[datetime]
    interview_location: Optional[str]
    screening_score: Optional[float]
    interview_score: Optional[float]
    technical_score: Optional[float]
    overall_rating: Optional[float]
    overall_score: Optional[float]
    recruiter_notes: Optional[str]
    rejection_reason: Optional[str]
    resume_file_path: Optional[str]
    cover_letter_file_path: Optional[str]
    is_active: bool
    application_date: date
    last_contact_date: Optional[date]
    days_in_stage: int
    created_at: datetime
    updated_at: Optional[datetime]


class ApplicationStageUpdate(BaseModel):
    """Schema for updating application stage"""
    stage: ApplicationStage
    notes: Optional[str] = None
    interview_date: Optional[datetime] = None
    interview_location: Optional[str] = None


class ApplicationEvaluation(BaseModel):
    """Schema for application evaluation"""
    screening_score: Optional[float] = None
    interview_score: Optional[float] = None
    technical_score: Optional[float] = None
    overall_rating: Optional[float] = None
    feedback: Optional[str] = None


class ApplicationSearch(BaseModel):
    """Job application search criteria"""
    query: Optional[str] = None
    position_applied: Optional[str] = None
    department: Optional[str] = None
    stage: Optional[ApplicationStage] = None
    source: Optional[ApplicationSource] = None
    priority: Optional[Priority] = None
    assigned_recruiter_id: Optional[uuid.UUID] = None
    application_date_from: Optional[date] = None
    application_date_to: Optional[date] = None
    is_active: Optional[bool] = True


class RecruitmentStats(BaseModel):
    """Recruitment statistics"""
    total_applications: int
    by_stage: Dict[str, int]
    by_source: Dict[str, int]
    by_department: Dict[str, int]
    average_time_to_hire: Optional[float]
    conversion_rates: Dict[str, float]
    top_positions: List[Dict[str, Any]]
    monthly_trends: Dict[str, int]