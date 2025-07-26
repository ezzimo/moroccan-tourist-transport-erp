"""
Driver-related Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from models.driver import Gender, LicenseType, EmploymentType, DriverStatus
import uuid


class DriverBase(BaseModel):
    """Base driver schema with common fields"""
    full_name: str = Field(..., min_length=2, max_length=255, description="Driver's full name")
    date_of_birth: date = Field(..., description="Driver's date of birth")
    gender: Gender = Field(..., description="Driver's gender")
    nationality: str = Field(default="Moroccan", max_length=100, description="Driver's nationality")
    national_id: str = Field(..., min_length=8, max_length=20, description="National ID number")
    
    # Contact Information
    phone: str = Field(..., min_length=10, max_length=20, description="Phone number")
    email: Optional[EmailStr] = Field(None, description="Email address")
    address: Optional[str] = Field(None, max_length=500, description="Home address")
    emergency_contact_name: Optional[str] = Field(None, max_length=255, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, max_length=20, description="Emergency contact phone")
    
    # Professional Information
    employee_id: Optional[str] = Field(None, max_length=20, description="Employee ID")
    employment_type: EmploymentType = Field(..., description="Type of employment")
    hire_date: date = Field(..., description="Date of hire")
    
    # License Information
    license_number: str = Field(..., min_length=6, max_length=50, description="Driving license number")
    license_type: LicenseType = Field(..., description="Type of driving license")
    license_issue_date: date = Field(..., description="License issue date")
    license_expiry_date: date = Field(..., description="License expiry date")
    license_issuing_authority: Optional[str] = Field(None, max_length=255, description="License issuing authority")
    
    # Health and Compliance
    health_certificate_expiry: Optional[date] = Field(None, description="Health certificate expiry date")
    medical_restrictions: Optional[str] = Field(None, max_length=500, description="Medical restrictions")
    
    # Skills and Certifications
    tour_guide_certified: bool = Field(default=False, description="Tour guide certification status")
    first_aid_certified: bool = Field(default=False, description="First aid certification status")
    
    # Additional Information
    notes: Optional[str] = Field(None, max_length=2000, description="Additional notes")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "full_name": "Ahmed Ben Ali",
                "date_of_birth": "1985-03-15",
                "gender": "Male",
                "nationality": "Moroccan",
                "national_id": "AB123456",
                "phone": "+212612345678",
                "email": "ahmed.benali@example.com",
                "address": "123 Rue Mohammed V, Casablanca",
                "emergency_contact_name": "Fatima Ben Ali",
                "emergency_contact_phone": "+212687654321",
                "employee_id": "EMP001",
                "employment_type": "Permanent",
                "hire_date": "2020-01-15",
                "license_number": "DL123456789",
                "license_type": "Category D",
                "license_issue_date": "2019-12-01",
                "license_expiry_date": "2025-12-01",
                "license_issuing_authority": "Prefecture de Casablanca",
                "health_certificate_expiry": "2024-06-30",
                "tour_guide_certified": True,
                "first_aid_certified": True,
                "notes": "Experienced driver with excellent customer service skills"
            }
        }


class DriverCreate(DriverBase):
    """Schema for creating a new driver"""
    languages_spoken: Optional[List[str]] = Field(default=[], description="List of languages spoken")
    
    @validator('date_of_birth')
    def validate_birth_date(cls, v):
        """Validate birth date"""
        if v >= date.today():
            raise ValueError('Birth date must be in the past')
        
        # Check minimum age (21 years for professional drivers)
        min_birth_date = date.today().replace(year=date.today().year - 21)
        if v > min_birth_date:
            raise ValueError('Driver must be at least 21 years old')
        
        # Check maximum age (65 years)
        max_birth_date = date.today().replace(year=date.today().year - 65)
        if v < max_birth_date:
            raise ValueError('Driver cannot be older than 65 years')
        
        return v
    
    @validator('license_expiry_date')
    def validate_license_expiry(cls, v, values):
        """Validate license expiry date"""
        if 'license_issue_date' in values and v <= values['license_issue_date']:
            raise ValueError('License expiry date must be after issue date')
        
        if v < date.today():
            raise ValueError('License must not be expired')
        
        return v
    
    @validator('hire_date')
    def validate_hire_date(cls, v):
        """Validate hire date"""
        # Allow future hire dates for planning
        max_future_date = date.today().replace(year=date.today().year + 1)
        if v > max_future_date:
            raise ValueError('Hire date cannot be more than 1 year in the future')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format"""
        import re
        # Morocco phone number pattern
        pattern = r'^\+212[5-7]\d{8}$|^0[5-7]\d{8}$'
        if not re.match(pattern, v.replace(' ', '').replace('-', '')):
            raise ValueError('Invalid Morocco phone number format')
        return v
    
    @validator('national_id')
    def validate_national_id(cls, v):
        """Validate Morocco national ID format"""
        import re
        pattern = r'^[A-Z]{1,2}[0-9]{6,8}$'
        if not re.match(pattern, v.upper()):
            raise ValueError('Invalid Morocco national ID format')
        return v.upper()
    
    @validator('license_number')
    def validate_license_number(cls, v):
        """Validate license number format"""
        import re
        pattern = r'^[A-Z0-9]{6,20}$'
        if not re.match(pattern, v.upper()):
            raise ValueError('Invalid license number format')
        return v.upper()


class DriverUpdate(BaseModel):
    """Schema for updating driver information"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    employee_id: Optional[str] = Field(None, max_length=20)
    employment_type: Optional[EmploymentType] = None
    license_expiry_date: Optional[date] = None
    license_issuing_authority: Optional[str] = Field(None, max_length=255)
    languages_spoken: Optional[List[str]] = None
    health_certificate_expiry: Optional[date] = None
    medical_restrictions: Optional[str] = Field(None, max_length=500)
    tour_guide_certified: Optional[bool] = None
    first_aid_certified: Optional[bool] = None
    status: Optional[DriverStatus] = None
    performance_rating: Optional[float] = Field(None, ge=0, le=5)
    notes: Optional[str] = Field(None, max_length=2000)

    class Config:
        from_attributes = True


class DriverResponse(DriverBase):
    """Schema for driver response with computed fields"""
    id: uuid.UUID
    languages_spoken: List[str] = []
    status: DriverStatus
    performance_rating: Optional[float] = Field(None, ge=0, le=5)
    total_tours_completed: int = Field(default=0, ge=0)
    total_incidents: int = Field(default=0, ge=0)
    profile_photo_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Computed fields
    age: int = Field(..., description="Driver's current age")
    years_of_service: float = Field(..., description="Years of service")
    is_license_expired: bool = Field(..., description="Whether license is expired")
    days_until_license_expiry: int = Field(..., description="Days until license expires")
    is_health_cert_expired: bool = Field(..., description="Whether health certificate is expired")
    days_until_health_cert_expiry: Optional[int] = Field(None, description="Days until health certificate expires")
    performance_score: float = Field(..., ge=0, le=5, description="Calculated performance score")
    is_available_for_assignment: bool = Field(..., description="Whether driver is available for assignments")

    class Config:
        from_attributes = True


class DriverSummary(BaseModel):
    """Driver summary for dashboard"""
    total_drivers: int = Field(..., ge=0)
    active_drivers: int = Field(..., ge=0)
    drivers_on_leave: int = Field(..., ge=0)
    suspended_drivers: int = Field(..., ge=0)
    license_expiring_soon: int = Field(..., ge=0)
    health_cert_expiring_soon: int = Field(..., ge=0)
    by_employment_type: Dict[str, int] = Field(default_factory=dict)
    by_license_type: Dict[str, int] = Field(default_factory=dict)
    average_performance_rating: float = Field(..., ge=0, le=5)
    total_tours_completed: int = Field(..., ge=0)
    total_incidents: int = Field(..., ge=0)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "total_drivers": 150,
                "active_drivers": 120,
                "drivers_on_leave": 15,
                "suspended_drivers": 5,
                "license_expiring_soon": 8,
                "health_cert_expiring_soon": 12,
                "by_employment_type": {
                    "Permanent": 100,
                    "Seasonal": 30,
                    "Contract": 20
                },
                "by_license_type": {
                    "Category D": 80,
                    "Category C": 40,
                    "Category B": 30
                },
                "average_performance_rating": 4.2,
                "total_tours_completed": 2500,
                "total_incidents": 45
            }
        }


class DriverSearch(BaseModel):
    """Driver search criteria"""
    query: Optional[str] = Field(None, description="Search query for name, license, or employee ID")
    status: Optional[DriverStatus] = None
    employment_type: Optional[EmploymentType] = None
    license_type: Optional[LicenseType] = None
    languages: Optional[List[str]] = None
    tour_guide_certified: Optional[bool] = None
    first_aid_certified: Optional[bool] = None
    available_for_assignment: Optional[bool] = None
    license_expiring_soon: Optional[bool] = None
    health_cert_expiring_soon: Optional[bool] = None
    min_age: Optional[int] = Field(None, ge=18, le=70)
    max_age: Optional[int] = Field(None, ge=18, le=70)
    min_experience_years: Optional[float] = Field(None, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Ahmed",
                "status": "Active",
                "employment_type": "Permanent",
                "license_type": "Category D",
                "languages": ["Arabic", "French", "English"],
                "tour_guide_certified": True,
                "available_for_assignment": True,
                "min_age": 25,
                "max_age": 55,
                "min_experience_years": 2.0
            }
        }


class DriverPerformance(BaseModel):
    """Driver performance metrics"""
    driver_id: uuid.UUID
    driver_name: str
    total_assignments: int = Field(..., ge=0)
    completed_assignments: int = Field(..., ge=0)
    completion_rate: float = Field(..., ge=0, le=100)
    average_customer_rating: Optional[float] = Field(None, ge=0, le=5)
    total_incidents: int = Field(..., ge=0)
    incident_rate: float = Field(..., ge=0)
    on_time_rate: float = Field(..., ge=0, le=100)
    performance_score: float = Field(..., ge=0, le=5)
    last_assignment_date: Optional[date] = None
    training_compliance_rate: float = Field(..., ge=0, le=100)
    customer_feedback_summary: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "driver_id": "123e4567-e89b-12d3-a456-426614174000",
                "driver_name": "Ahmed Ben Ali",
                "total_assignments": 150,
                "completed_assignments": 145,
                "completion_rate": 96.7,
                "average_customer_rating": 4.5,
                "total_incidents": 2,
                "incident_rate": 1.3,
                "on_time_rate": 94.5,
                "performance_score": 4.3,
                "last_assignment_date": "2024-01-15",
                "training_compliance_rate": 100.0,
                "customer_feedback_summary": "Excellent driver with great knowledge of local attractions"
            }
        }


class DriverAvailability(BaseModel):
    """Driver availability status"""
    driver_id: uuid.UUID
    driver_name: str
    is_available: bool
    availability_reason: str
    next_available_date: Optional[date] = None
    current_assignment_id: Optional[uuid.UUID] = None
    restrictions: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


class DriverComplianceStatus(BaseModel):
    """Driver compliance status"""
    driver_id: uuid.UUID
    driver_name: str
    license_status: str = Field(..., description="License compliance status")
    health_cert_status: str = Field(..., description="Health certificate status")
    training_status: str = Field(..., description="Training compliance status")
    document_status: str = Field(..., description="Document compliance status")
    overall_compliance_score: float = Field(..., ge=0, le=100)
    compliance_issues: List[str] = Field(default_factory=list)
    next_renewal_date: Optional[date] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "driver_id": "123e4567-e89b-12d3-a456-426614174000",
                "driver_name": "Ahmed Ben Ali",
                "license_status": "Valid",
                "health_cert_status": "Expires Soon",
                "training_status": "Up to Date",
                "document_status": "Complete",
                "overall_compliance_score": 85.0,
                "compliance_issues": ["Health certificate expires in 15 days"],
                "next_renewal_date": "2024-02-15"
            }
        }