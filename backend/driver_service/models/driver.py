"""
Driver model for driver management
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
import uuid


class Gender(str, Enum):
    """Gender enumeration"""
    MALE = "Male"
    FEMALE = "Female"


class LicenseType(str, Enum):
    """Driver license type enumeration"""
    CATEGORY_B = "Category B"  # Cars, light vehicles
    CATEGORY_C = "Category C"  # Trucks, heavy vehicles
    CATEGORY_D = "Category D"  # Buses, passenger transport
    CATEGORY_D1 = "Category D1"  # Minibuses
    PROFESSIONAL = "Professional"  # Professional driver license


class EmploymentType(str, Enum):
    """Employment type enumeration"""
    PERMANENT = "Permanent"
    SEASONAL = "Seasonal"
    CONTRACT = "Contract"
    FREELANCE = "Freelance"


class DriverStatus(str, Enum):
    """Driver status enumeration"""
    ACTIVE = "Active"
    ON_LEAVE = "On Leave"
    IN_TRAINING = "In Training"
    SUSPENDED = "Suspended"
    TERMINATED = "Terminated"
    RETIRED = "Retired"


class Driver(SQLModel, table=True):
    """Driver model for managing professional drivers"""
    __tablename__ = "drivers"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Personal Information
    full_name: str = Field(max_length=255, index=True)
    date_of_birth: date = Field(index=True)
    gender: Gender
    nationality: str = Field(default="Moroccan", max_length=100)
    national_id: str = Field(unique=True, max_length=20, index=True)
    
    # Contact Information
    phone: str = Field(max_length=20, index=True)
    email: Optional[str] = Field(default=None, max_length=255)
    address: Optional[str] = Field(default=None, max_length=500)
    emergency_contact_name: Optional[str] = Field(default=None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(default=None, max_length=20)
    
    # Professional Information
    employee_id: Optional[str] = Field(default=None, max_length=20, index=True)
    employment_type: EmploymentType = Field(index=True)
    hire_date: date = Field(index=True)
    
    # License Information
    license_number: str = Field(unique=True, max_length=50, index=True)
    license_type: LicenseType = Field(index=True)
    license_issue_date: date
    license_expiry_date: date = Field(index=True)
    license_issuing_authority: Optional[str] = Field(default=None, max_length=255)
    
    # Languages and Skills
    languages_spoken: Optional[str] = Field(default=None, max_length=200)  # JSON string
    tour_guide_certified: bool = Field(default=False)
    first_aid_certified: bool = Field(default=False)
    
    # Health and Compliance
    health_certificate_expiry: Optional[date] = Field(default=None, index=True)
    medical_restrictions: Optional[str] = Field(default=None, max_length=500)
    
    # Status and Performance
    status: DriverStatus = Field(default=DriverStatus.ACTIVE, index=True)
    performance_rating: Optional[float] = Field(default=None, ge=0, le=5)
    total_tours_completed: int = Field(default=0, ge=0)
    total_incidents: int = Field(default=0, ge=0)
    
    # Documents and Media
    profile_photo_path: Optional[str] = Field(default=None, max_length=500)
    
    # Additional Information
    notes: Optional[str] = Field(default=None, max_length=2000)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    assignments: List["DriverAssignment"] = Relationship(back_populates="driver")
    training_records: List["DriverTrainingRecord"] = Relationship(back_populates="driver")
    incidents: List["DriverIncident"] = Relationship(back_populates="driver")
    documents: List["DriverDocument"] = Relationship(back_populates="driver")
    
    def get_age(self) -> int:
        """Calculate driver age"""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def get_years_of_service(self) -> float:
        """Calculate years of service"""
        service_days = (date.today() - self.hire_date).days
        return round(service_days / 365.25, 2)
    
    def is_license_expired(self) -> bool:
        """Check if license is expired"""
        return date.today() > self.license_expiry_date
    
    def days_until_license_expiry(self) -> int:
        """Get days until license expires"""
        return (self.license_expiry_date - date.today()).days
    
    def is_health_cert_expired(self) -> bool:
        """Check if health certificate is expired"""
        if not self.health_certificate_expiry:
            return False
        return date.today() > self.health_certificate_expiry
    
    def days_until_health_cert_expiry(self) -> Optional[int]:
        """Get days until health certificate expires"""
        if not self.health_certificate_expiry:
            return None
        return (self.health_certificate_expiry - date.today()).days
    
    def get_languages_list(self) -> List[str]:
        """Parse languages from JSON string"""
        if not self.languages_spoken:
            return []
        try:
            import json
            return json.loads(self.languages_spoken)
        except:
            return []
    
    def set_languages_list(self, languages: List[str]):
        """Set languages as JSON string"""
        import json
        self.languages_spoken = json.dumps(languages) if languages else None
    
    def calculate_performance_score(self) -> float:
        """Calculate overall performance score"""
        if self.total_tours_completed == 0:
            return 0.0
        
        # Base score from rating
        base_score = self.performance_rating or 3.0
        
        # Adjust for incident rate
        incident_rate = self.total_incidents / self.total_tours_completed
        incident_penalty = min(incident_rate * 2, 2.0)  # Max 2 point penalty
        
        # Adjust for experience
        experience_bonus = min(self.get_years_of_service() * 0.1, 0.5)  # Max 0.5 bonus
        
        final_score = base_score - incident_penalty + experience_bonus
        return max(0.0, min(5.0, final_score))
    
    def is_available_for_assignment(self) -> bool:
        """Check if driver is available for new assignments"""
        return (
            self.status == DriverStatus.ACTIVE and
            not self.is_license_expired() and
            not self.is_health_cert_expired()
        )