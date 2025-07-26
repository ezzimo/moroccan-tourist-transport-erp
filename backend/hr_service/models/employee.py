"""
Employee model for HR management
"""
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
import uuid


class Gender(str, Enum):
    """Gender enumeration"""
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class MaritalStatus(str, Enum):
    """Marital status enumeration"""
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"


class EmploymentType(str, Enum):
    """Employment type enumeration"""
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    CONTRACT = "Contract"
    TEMPORARY = "Temporary"
    INTERN = "Intern"


class ContractType(str, Enum):
    """Contract type enumeration"""
    PERMANENT = "Permanent"
    FIXED_TERM = "Fixed Term"
    PROBATION = "Probation"
    SEASONAL = "Seasonal"


class EmployeeStatus(str, Enum):
    """Employee status enumeration"""
    ACTIVE = "Active"
    PROBATION = "Probation"
    SUSPENDED = "Suspended"
    TERMINATED = "Terminated"
    RESIGNED = "Resigned"
    RETIRED = "Retired"


class Employee(SQLModel, table=True):
    """Employee model for HR management"""
    __tablename__ = "employees"
    
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    
    # Personal Information
    employee_id: str = Field(unique=True, max_length=20, index=True)
    full_name: str = Field(max_length=255, index=True)
    national_id: str = Field(unique=True, max_length=20, index=True)
    
    # Demographics
    gender: Gender = Field(index=True)
    birth_date: date = Field(index=True)
    marital_status: MaritalStatus = Field(default=MaritalStatus.SINGLE)
    
    # Contact Information
    email: str = Field(unique=True, max_length=255, index=True)
    phone: str = Field(max_length=20)
    address: Optional[str] = Field(default=None, max_length=500)
    emergency_contact_name: Optional[str] = Field(default=None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(default=None, max_length=20)
    
    # Employment Details
    department: str = Field(max_length=100, index=True)
    position: str = Field(max_length=100, index=True)
    employment_type: EmploymentType = Field(index=True)
    contract_type: ContractType = Field(index=True)
    
    # Employment Dates
    hire_date: date = Field(index=True)
    contract_start_date: date = Field(index=True)
    contract_end_date: Optional[date] = Field(default=None, index=True)
    probation_end_date: Optional[date] = Field(default=None)
    
    # Compensation
    base_salary: Decimal = Field(sa_column=Column(Numeric(12, 2)))
    currency: str = Field(default="MAD", max_length=3)
    
    # Benefits and Tax
    social_security_number: Optional[str] = Field(default=None, max_length=50)
    tax_id: Optional[str] = Field(default=None, max_length=50)
    bank_account: Optional[str] = Field(default=None, max_length=50)
    
    # Status and Management
    status: EmployeeStatus = Field(default=EmployeeStatus.PROBATION, index=True)
    manager_id: Optional[uuid.UUID] = Field(default=None, foreign_key="employees.id")
    
    # Additional Information
    notes: Optional[str] = Field(default=None, max_length=2000)
    is_active: bool = Field(default=True, index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    termination_date: Optional[datetime] = Field(default=None)
    
    # Relationships
    manager: Optional["Employee"] = Relationship(
        back_populates="direct_reports",
        sa_relationship_kwargs={"remote_side": "Employee.id"}
    )
    direct_reports: List["Employee"] = Relationship(back_populates="manager")
    documents: List["EmployeeDocument"] = Relationship(back_populates="employee")
    training_records: List["EmployeeTraining"] = Relationship(back_populates="employee")
    
    def get_age(self) -> int:
        """Calculate employee age"""
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
    
    def get_years_of_service(self) -> float:
        """Calculate years of service"""
        end_date = self.termination_date.date() if self.termination_date else date.today()
        service_days = (end_date - self.hire_date).days
        return round(service_days / 365.25, 2)
    
    def is_on_probation(self) -> bool:
        """Check if employee is still on probation"""
        if not self.probation_end_date:
            return False
        return date.today() <= self.probation_end_date
    
    def get_display_name(self) -> str:
        """Get display name for the employee"""
        return f"{self.full_name} ({self.employee_id})"
    
    def calculate_monthly_salary(self) -> Decimal:
        """Calculate monthly salary"""
        return self.base_salary / 12