"""
Driver-related Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from models.driver import Gender, LicenseType, EmploymentType, DriverStatus
import uuid


class DriverBase(BaseModel):
    full_name: str
    date_of_birth: date
    gender: Gender
    nationality: str = "Moroccan"
    national_id: str
    phone: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    employee_id: Optional[str] = None
    employment_type: EmploymentType
    hire_date: date
    license_number: str
    license_type: LicenseType
    license_issue_date: date
    license_expiry_date: date
    license_issuing_authority: Optional[str] = None
    health_certificate_expiry: Optional[date] = None
    medical_restrictions: Optional[str] = None
    tour_guide_certified: bool = False
    first_aid_certified: bool = False
    notes: Optional[str] = None


class DriverCreate(DriverBase):
    languages_spoken: Optional[List[str]] = []
    
    @validator('date_of_birth')
    def validate_birth_date(cls, v):
        if v >= date.today():
            raise ValueError('Birth date must be in the past')
        
        # Check minimum age (21 years for professional drivers)
        min_birth_date = date.today().replace(year=date.today().year - 21)
        if v > min_birth_date:
            raise ValueError('Driver must be at least 21 years old')
        
        return v
    
    @validator('license_expiry_date')
    def validate_license_expiry(cls, v, values):
        if 'license_issue_date' in values and v <= values['license_issue_date']:
            raise ValueError('License expiry date must be after issue date')
        
        if v < date.today():
            raise ValueError('License must not be expired')
        
        return v
    
    @validator('hire_date')
    def validate_hire_date(cls, v):
        # Allow future hire dates for planning
        max_future_date = date.today().replace(year=date.today().year + 1)
        if v > max_future_date:
            raise ValueError('Hire date cannot be more than 1 year in the future')
        return v


class DriverUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    employee_id: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    license_expiry_date: Optional[date] = None
    license_issuing_authority: Optional[str] = None
    languages_spoken: Optional[List[str]] = None
    health_certificate_expiry: Optional[date] = None
    medical_restrictions: Optional[str] = None
    tour_guide_certified: Optional[bool] = None
    first_aid_certified: Optional[bool] = None
    status: Optional[DriverStatus] = None
    performance_rating: Optional[float] = None
    notes: Optional[str] = None


class DriverResponse(DriverBase):
    id: uuid.UUID
    languages_spoken: List[str] = []
    status: DriverStatus
    performance_rating: Optional[float]
    total_tours_completed: int
    total_incidents: int
    profile_photo_path: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    age: int
    years_of_service: float
    is_license_expired: bool
    days_until_license_expiry: int
    is_health_cert_expired: bool
    days_until_health_cert_expiry: Optional[int]
    performance_score: float
    is_available_for_assignment: bool


class DriverSummary(BaseModel):
    """Driver summary for dashboard"""
    total_drivers: int
    active_drivers: int
    drivers_on_leave: int
    suspended_drivers: int
    license_expiring_soon: int
    health_cert_expiring_soon: int
    by_employment_type: Dict[str, int]
    by_license_type: Dict[str, int]
    average_performance_rating: float
    total_tours_completed: int
    total_incidents: int


class DriverSearch(BaseModel):
    """Driver search criteria"""
    query: Optional[str] = None
    status: Optional[DriverStatus] = None
    employment_type: Optional[EmploymentType] = None
    license_type: Optional[LicenseType] = None
    languages: Optional[List[str]] = None
    tour_guide_certified: Optional[bool] = None
    first_aid_certified: Optional[bool] = None
    available_for_assignment: Optional[bool] = None
    license_expiring_soon: Optional[bool] = None
    health_cert_expiring_soon: Optional[bool] = None


class DriverPerformance(BaseModel):
    """Driver performance metrics"""
    driver_id: uuid.UUID
    driver_name: str
    total_assignments: int
    completed_assignments: int
    completion_rate: float
    average_customer_rating: Optional[float]
    total_incidents: int
    incident_rate: float
    on_time_rate: float
    performance_score: float
    last_assignment_date: Optional[date]