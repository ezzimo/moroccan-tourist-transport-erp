"""
Job application model for recruitment tracking
"""
from sqlmodel import SQLModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
import uuid


class ApplicationSource(str, Enum):
    """Application source enumeration"""
    JOB_BOARD = "Job Board"
    COMPANY_WEBSITE = "Company Website"
    REFERRAL = "Referral"
    RECRUITMENT_AGENCY = "Recruitment Agency"
    SOCIAL_MEDIA = "Social Media"
    WALK_IN = "Walk In"
    OTHER = "Other"


class ApplicationStage(str, Enum):
    """Application stage enumeration"""
    RECEIVED = "Received"
    SCREENING = "Screening"
    PHONE_INTERVIEW = "Phone Interview"
    TECHNICAL_TEST = "Technical Test"
    IN_PERSON_INTERVIEW = "In-Person Interview"
    REFERENCE_CHECK = "Reference Check"
    OFFER_MADE = "Offer Made"
    OFFER_ACCEPTED = "Offer Accepted"
    HIRED = "Hired"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"


class Priority(str, Enum):
    """Application priority enumeration"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"


class JobApplication(SQLModel, table=True):
    """Job application model for recruitment tracking"""
    __tablename__ = "job_applications"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Applicant Information
    full_name: str = Field(max_length=255, index=True)
    email: str = Field(max_length=255, index=True)
    phone: str = Field(max_length=20)
    national_id: Optional[str] = Field(default=None, max_length=20)
    
    # Application Details
    position_applied: str = Field(max_length=100, index=True)
    department: str = Field(max_length=100, index=True)
    source: ApplicationSource = Field(index=True)
    stage: ApplicationStage = Field(default=ApplicationStage.RECEIVED, index=True)
    priority: Priority = Field(default=Priority.MEDIUM, index=True)
    
    # Experience and Qualifications
    years_of_experience: Optional[int] = Field(default=None, ge=0)
    education_level: Optional[str] = Field(default=None, max_length=100)
    languages: Optional[str] = Field(default=None, max_length=200)  # JSON string
    skills: Optional[str] = Field(default=None, max_length=500)     # JSON string
    
    # Salary Expectations
    expected_salary: Optional[float] = Field(default=None, ge=0)
    currency: str = Field(default="MAD", max_length=3)
    
    # Documents
    resume_file_path: Optional[str] = Field(default=None, max_length=500)
    cover_letter_file_path: Optional[str] = Field(default=None, max_length=500)
    
    # Assignment and Tracking
    assigned_recruiter_id: Optional[uuid.UUID] = Field(default=None, index=True)
    interview_date: Optional[datetime] = Field(default=None)
    interview_location: Optional[str] = Field(default=None, max_length=255)
    
    # Evaluation
    screening_score: Optional[float] = Field(default=None, ge=0, le=100)
    interview_score: Optional[float] = Field(default=None, ge=0, le=100)
    technical_score: Optional[float] = Field(default=None, ge=0, le=100)
    overall_rating: Optional[float] = Field(default=None, ge=0, le=10)
    
    # Notes and Feedback
    recruiter_notes: Optional[str] = Field(default=None, max_length=2000)
    rejection_reason: Optional[str] = Field(default=None, max_length=500)
    
    # Status
    is_active: bool = Field(default=True, index=True)
    
    # Timestamps
    application_date: date = Field(default_factory=date.today, index=True)
    last_contact_date: Optional[date] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    def get_languages_list(self) -> List[str]:
        """Parse languages from JSON string"""
        if not self.languages:
            return []
        try:
            import json
            return json.loads(self.languages)
        except:
            return []
    
    def set_languages_list(self, languages: List[str]):
        """Set languages as JSON string"""
        import json
        self.languages = json.dumps(languages) if languages else None
    
    def get_skills_list(self) -> List[str]:
        """Parse skills from JSON string"""
        if not self.skills:
            return []
        try:
            import json
            return json.loads(self.skills)
        except:
            return []
    
    def set_skills_list(self, skills: List[str]):
        """Set skills as JSON string"""
        import json
        self.skills = json.dumps(skills) if skills else None
    
    def calculate_overall_score(self) -> Optional[float]:
        """Calculate overall score from individual scores"""
        scores = [
            score for score in [self.screening_score, self.interview_score, self.technical_score]
            if score is not None
        ]
        
        if not scores:
            return None
        
        return round(sum(scores) / len(scores), 2)
    
    def get_days_in_stage(self) -> int:
        """Get number of days in current stage"""
        return (date.today() - self.application_date).days