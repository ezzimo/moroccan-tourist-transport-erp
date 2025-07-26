"""
Data validation utilities for HR service
"""
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status, UploadFile
import re
import logging

logger = logging.getLogger(__name__)

# Validation patterns
PHONE_PATTERN = re.compile(r'^\+?[1-9]\d{1,14}$')  # E.164 format
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
NATIONAL_ID_PATTERN = re.compile(r'^[A-Z]{1,2}[0-9]{6,8}$')  # Morocco national ID


class ValidationError(Exception):
    """Custom validation error"""
    pass


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format
    
    Args:
        phone: Phone number string
        
    Returns:
        True if valid
    """
    if not phone:
        return False
    
    # Remove spaces and dashes
    clean_phone = re.sub(r'[\s-]', '', phone)
    return bool(PHONE_PATTERN.match(clean_phone))


def validate_email(email: str) -> bool:
    """Validate email format
    
    Args:
        email: Email string
        
    Returns:
        True if valid
    """
    if not email:
        return False
    return bool(EMAIL_PATTERN.match(email.lower()))


def validate_national_id(national_id: str) -> bool:
    """Validate Morocco national ID format
    
    Args:
        national_id: National ID string
        
    Returns:
        True if valid
    """
    if not national_id:
        return False
    return bool(NATIONAL_ID_PATTERN.match(national_id.upper()))


def validate_age(date_of_birth: date, min_age: int = 18, max_age: int = 70) -> bool:
    """Validate employee age
    
    Args:
        date_of_birth: Date of birth
        min_age: Minimum age requirement
        max_age: Maximum age requirement
        
    Returns:
        True if valid
    """
    today = date.today()
    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    return min_age <= age <= max_age


def validate_salary(salary: float, min_salary: float = 2000.0) -> bool:
    """Validate salary amount (Morocco minimum wage consideration)
    
    Args:
        salary: Salary amount
        min_salary: Minimum salary (MAD 2000 ~ Morocco minimum wage)
        
    Returns:
        True if valid
    """
    return salary >= min_salary


def validate_contract_dates(start_date: date, end_date: Optional[date] = None) -> bool:
    """Validate contract dates
    
    Args:
        start_date: Contract start date
        end_date: Contract end date (optional for permanent contracts)
        
    Returns:
        True if valid
    """
    # Start date should not be too far in the past or future
    min_start_date = date.today() - timedelta(days=365 * 10)  # 10 years ago
    max_start_date = date.today() + timedelta(days=365)  # 1 year in future
    
    if not (min_start_date <= start_date <= max_start_date):
        return False
    
    # If end date is provided, it should be after start date
    if end_date and end_date <= start_date:
        return False
    
    return True


def validate_employee_data(employee_data: Dict[str, Any]) -> List[str]:
    """Validate employee data comprehensively
    
    Args:
        employee_data: Employee data dictionary
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ['full_name', 'email', 'phone', 'position', 'start_date']
    for field in required_fields:
        if not employee_data.get(field):
            errors.append(f"{field} is required")
    
    # Email validation
    if employee_data.get('email') and not validate_email(employee_data['email']):
        errors.append("Invalid email format")
    
    # Phone validation
    if employee_data.get('phone') and not validate_phone_number(employee_data['phone']):
        errors.append("Invalid phone number format")
    
    # National ID validation
    if employee_data.get('national_id') and not validate_national_id(employee_data['national_id']):
        errors.append("Invalid national ID format")
    
    # Age validation
    if employee_data.get('date_of_birth'):
        try:
            dob = employee_data['date_of_birth']
            if isinstance(dob, str):
                dob = datetime.strptime(dob, '%Y-%m-%d').date()
            if not validate_age(dob):
                errors.append("Employee age must be between 18 and 70 years")
        except (ValueError, TypeError):
            errors.append("Invalid date of birth format")
    
    # Salary validation
    if employee_data.get('salary'):
        try:
            salary = float(employee_data['salary'])
            if not validate_salary(salary):
                errors.append("Salary must be at least MAD 2000 (minimum wage)")
        except (ValueError, TypeError):
            errors.append("Invalid salary format")
    
    # Contract dates validation
    if employee_data.get('start_date'):
        try:
            start_date = employee_data['start_date']
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            end_date = employee_data.get('end_date')
            if end_date and isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if not validate_contract_dates(start_date, end_date):
                errors.append("Invalid contract dates")
        except (ValueError, TypeError):
            errors.append("Invalid date format for contract dates")
    
    return errors


def validate_job_application_data(application_data: Dict[str, Any]) -> List[str]:
    """Validate job application data
    
    Args:
        application_data: Job application data
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ['full_name', 'email', 'phone', 'position_applied']
    for field in required_fields:
        if not application_data.get(field):
            errors.append(f"{field} is required")
    
    # Email validation
    if application_data.get('email') and not validate_email(application_data['email']):
        errors.append("Invalid email format")
    
    # Phone validation
    if application_data.get('phone') and not validate_phone_number(application_data['phone']):
        errors.append("Invalid phone number format")
    
    # Expected salary validation
    if application_data.get('expected_salary'):
        try:
            salary = float(application_data['expected_salary'])
            if salary < 0:
                errors.append("Expected salary cannot be negative")
        except (ValueError, TypeError):
            errors.append("Invalid expected salary format")
    
    # Availability date validation
    if application_data.get('availability_date'):
        try:
            avail_date = application_data['availability_date']
            if isinstance(avail_date, str):
                avail_date = datetime.strptime(avail_date, '%Y-%m-%d').date()
            
            # Should not be more than 6 months in the future
            max_availability = date.today() + timedelta(days=180)
            if avail_date > max_availability:
                errors.append("Availability date cannot be more than 6 months in the future")
        except (ValueError, TypeError):
            errors.append("Invalid availability date format")
    
    return errors


def validate_training_data(training_data: Dict[str, Any]) -> List[str]:
    """Validate training program data
    
    Args:
        training_data: Training program data
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ['title', 'start_date', 'end_date']
    for field in required_fields:
        if not training_data.get(field):
            errors.append(f"{field} is required")
    
    # Date validation
    if training_data.get('start_date') and training_data.get('end_date'):
        try:
            start_date = training_data['start_date']
            end_date = training_data['end_date']
            
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if end_date <= start_date:
                errors.append("End date must be after start date")
            
            # Training should not be scheduled more than 1 year in advance
            max_future_date = date.today() + timedelta(days=365)
            if start_date > max_future_date:
                errors.append("Training cannot be scheduled more than 1 year in advance")
                
        except (ValueError, TypeError):
            errors.append("Invalid date format")
    
    # Cost validation
    if training_data.get('cost') is not None:
        try:
            cost = float(training_data['cost'])
            if cost < 0:
                errors.append("Training cost cannot be negative")
        except (ValueError, TypeError):
            errors.append("Invalid cost format")
    
    # Max participants validation
    if training_data.get('max_participants') is not None:
        try:
            max_participants = int(training_data['max_participants'])
            if max_participants <= 0:
                errors.append("Maximum participants must be greater than 0")
            elif max_participants > 100:
                errors.append("Maximum participants cannot exceed 100")
        except (ValueError, TypeError):
            errors.append("Invalid max participants format")
    
    return errors


async def validate_document(file: UploadFile) -> Dict[str, Any]:
    """Validate document upload
    
    Args:
        file: Uploaded file
        
    Returns:
        Validation results
        
    Raises:
        HTTPException: If validation fails
    """
    # File size check
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # File extension check
    allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'}
    file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if f'.{file_ext}' not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type .{file_ext} not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Read a small portion to check if file is not corrupted
    try:
        content_sample = await file.read(1024)  # Read first 1KB
        await file.seek(0)  # Reset file pointer
        
        if not content_sample:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File appears to be empty or corrupted"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading file: {str(e)}"
        )
    
    return {
        "filename": file.filename,
        "size": file.size,
        "content_type": file.content_type,
        "extension": file_ext
    }


def validate_evaluation_score(score: float) -> bool:
    """Validate training evaluation score
    
    Args:
        score: Evaluation score
        
    Returns:
        True if valid (0-100 range)
    """
    return 0 <= score <= 100


def validate_morocco_business_rules(employee_data: Dict[str, Any]) -> List[str]:
    """Validate Morocco-specific business rules
    
    Args:
        employee_data: Employee data
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Morocco labor law considerations
    
    # Working hours validation (Morocco: 44 hours/week max)
    if employee_data.get('weekly_hours'):
        try:
            weekly_hours = float(employee_data['weekly_hours'])
            if weekly_hours > 44:
                errors.append("Weekly working hours cannot exceed 44 hours (Morocco labor law)")
        except (ValueError, TypeError):
            errors.append("Invalid weekly hours format")
    
    # Vacation days (Morocco: minimum 18 days/year)
    if employee_data.get('annual_leave_days'):
        try:
            leave_days = int(employee_data['annual_leave_days'])
            if leave_days < 18:
                errors.append("Annual leave days must be at least 18 days (Morocco labor law)")
        except (ValueError, TypeError):
            errors.append("Invalid annual leave days format")
    
    # Social security number validation (CNSS)
    if employee_data.get('social_security_number'):
        cnss_number = employee_data['social_security_number']
        # Morocco CNSS number is typically 10 digits
        if not re.match(r'^\d{10}$', cnss_number):
            errors.append("Invalid CNSS (social security) number format")
    
    return errors


def raise_validation_error(errors: List[str]) -> None:
    """Raise HTTP exception for validation errors
    
    Args:
        errors: List of validation error messages
    """
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Validation failed",
                "errors": errors
            }
        )