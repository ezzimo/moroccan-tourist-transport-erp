"""
Employee-related Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from models.employee import (
    Gender, MaritalStatus, EmploymentType, ContractType, EmployeeStatus
)
import uuid


class EmployeeBase(BaseModel):
    employee_id: str
    full_name: str
    national_id: str
    gender: Gender
    birth_date: date
    marital_status: MaritalStatus = MaritalStatus.SINGLE
    email: EmailStr
    phone: str
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    department: str
    position: str
    employment_type: EmploymentType
    contract_type: ContractType
    hire_date: date
    contract_start_date: date
    contract_end_date: Optional[date] = None
    base_salary: Decimal
    social_security_number: Optional[str] = None
    tax_id: Optional[str] = None
    bank_account: Optional[str] = None
    manager_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    @validator('birth_date')
    def validate_birth_date(cls, v):
        if v >= date.today():
            raise ValueError('Birth date must be in the past')
        
        # Check minimum age (18 years)
        min_birth_date = date.today().replace(year=date.today().year - 18)
        if v > min_birth_date:
            raise ValueError('Employee must be at least 18 years old')
        
        return v
    
    @validator('hire_date')
    def validate_hire_date(cls, v):
        # Allow future hire dates for planning
        max_future_date = date.today().replace(year=date.today().year + 1)
        if v > max_future_date:
            raise ValueError('Hire date cannot be more than 1 year in the future')
        return v
    
    @validator('contract_end_date')
    def validate_contract_dates(cls, v, values):
        if v and 'contract_start_date' in values:
            if v <= values['contract_start_date']:
                raise ValueError('Contract end date must be after start date')
        return v
    
    @validator('base_salary')
    def validate_salary(cls, v):
        if v <= 0:
            raise ValueError('Base salary must be greater than 0')
        # Morocco minimum wage check (approximate)
        if v < 2500:  # MAD per month
            raise ValueError('Salary cannot be below minimum wage')
        return v


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    contract_type: Optional[ContractType] = None
    contract_end_date: Optional[date] = None
    base_salary: Optional[Decimal] = None
    social_security_number: Optional[str] = None
    tax_id: Optional[str] = None
    bank_account: Optional[str] = None
    manager_id: Optional[uuid.UUID] = None
    status: Optional[EmployeeStatus] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class EmployeeResponse(EmployeeBase):
    id: uuid.UUID
    status: EmployeeStatus
    probation_end_date: Optional[date]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    termination_date: Optional[datetime]
    age: int
    years_of_service: float
    is_on_probation: bool
    display_name: str
    monthly_salary: Decimal


class EmployeeSummary(EmployeeResponse):
    """Extended employee response with summary statistics"""
    total_training_hours: int = 0
    completed_trainings: int = 0
    pending_trainings: int = 0
    certificates_count: int = 0
    documents_count: int = 0
    manager_name: Optional[str] = None
    direct_reports_count: int = 0
    last_training_date: Optional[date] = None
    next_training_date: Optional[date] = None
    performance_rating: Optional[float] = None


class EmployeeSearch(BaseModel):
    """Employee search criteria"""
    query: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    contract_type: Optional[ContractType] = None
    status: Optional[EmployeeStatus] = None
    manager_id: Optional[uuid.UUID] = None
    hire_date_from: Optional[date] = None
    hire_date_to: Optional[date] = None
    is_active: Optional[bool] = True


class EmployeeTermination(BaseModel):
    """Schema for employee termination"""
    termination_date: date
    reason: str
    notice_period_days: Optional[int] = None
    final_pay_amount: Optional[Decimal] = None
    return_company_property: bool = True
    exit_interview_completed: bool = False
    notes: Optional[str] = None