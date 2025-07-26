"""
Data validation utilities for driver service
"""
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from fastapi import HTTPException, status
from models.driver import Driver, DriverStatus, LicenseType
from models.driver_assignment import DriverAssignment, AssignmentStatus
from models.driver_training import DriverTrainingRecord
import re
import logging

logger = logging.getLogger(__name__)

# Validation patterns
PHONE_PATTERN = re.compile(r'^\+?[1-9]\d{1,14}$')  # E.164 format
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
LICENSE_PATTERN = re.compile(r'^[A-Z0-9]{6,20}$')  # Morocco license format
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


def validate_license_number(license_number: str) -> bool:
    """Validate Morocco driving license number format
    
    Args:
        license_number: License number string
        
    Returns:
        True if valid
    """
    if not license_number:
        return False
    return bool(LICENSE_PATTERN.match(license_number.upper()))


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


def validate_age(date_of_birth: date, min_age: int = 21, max_age: int = 65) -> bool:
    """Validate driver age
    
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


def validate_license_expiry(license_expiry: date, min_validity_months: int = 6) -> bool:
    """Validate license expiry date
    
    Args:
        license_expiry: License expiry date
        min_validity_months: Minimum validity period in months
        
    Returns:
        True if valid
    """
    min_expiry = date.today() + timedelta(days=min_validity_months * 30)
    return license_expiry >= min_expiry


def validate_languages(languages: List[str]) -> bool:
    """Validate languages list
    
    Args:
        languages: List of language codes
        
    Returns:
        True if valid
    """
    if not languages:
        return True  # Optional field
    
    # Common language codes for Morocco
    valid_languages = {
        'ar', 'fr', 'en', 'es', 'de', 'it', 'pt', 'ru', 'zh', 'ja',
        'arabic', 'french', 'english', 'spanish', 'german', 'italian',
        'portuguese', 'russian', 'chinese', 'japanese', 'berber', 'tamazight'
    }
    
    return all(lang.lower() in valid_languages for lang in languages)


def validate_driver_data(driver_data: Dict[str, Any]) -> List[str]:
    """Validate driver data comprehensively
    
    Args:
        driver_data: Driver data dictionary
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ['full_name', 'date_of_birth', 'phone', 'license_number', 'license_expiry_date']
    for field in required_fields:
        if not driver_data.get(field):
            errors.append(f"{field} is required")
    
    # Phone validation
    if driver_data.get('phone') and not validate_phone_number(driver_data['phone']):
        errors.append("Invalid phone number format")
    
    # Email validation
    if driver_data.get('email') and not validate_email(driver_data['email']):
        errors.append("Invalid email format")
    
    # License number validation
    if driver_data.get('license_number') and not validate_license_number(driver_data['license_number']):
        errors.append("Invalid license number format")
    
    # National ID validation
    if driver_data.get('national_id') and not validate_national_id(driver_data['national_id']):
        errors.append("Invalid national ID format")
    
    # Age validation
    if driver_data.get('date_of_birth'):
        try:
            dob = driver_data['date_of_birth']
            if isinstance(dob, str):
                dob = datetime.strptime(dob, '%Y-%m-%d').date()
            if not validate_age(dob):
                errors.append("Driver age must be between 21 and 65 years")
        except (ValueError, TypeError):
            errors.append("Invalid date of birth format")
    
    # License expiry validation
    if driver_data.get('license_expiry_date'):
        try:
            expiry = driver_data['license_expiry_date']
            if isinstance(expiry, str):
                expiry = datetime.strptime(expiry, '%Y-%m-%d').date()
            if not validate_license_expiry(expiry):
                errors.append("License must be valid for at least 6 months")
        except (ValueError, TypeError):
            errors.append("Invalid license expiry date format")
    
    # Languages validation
    if driver_data.get('languages_spoken') and not validate_languages(driver_data['languages_spoken']):
        errors.append("Invalid language codes")
    
    return errors


def validate_assignment_conflict(
    session: Session,
    driver_id: str,
    start_date: date,
    end_date: date,
    exclude_assignment_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Check for assignment conflicts
    
    Args:
        session: Database session
        driver_id: Driver UUID
        start_date: Assignment start date
        end_date: Assignment end date
        exclude_assignment_id: Assignment ID to exclude from conflict check
        
    Returns:
        List of conflicting assignments
    """
    # Build query for overlapping assignments
    query = select(DriverAssignment).where(
        DriverAssignment.driver_id == driver_id,
        DriverAssignment.status.in_([AssignmentStatus.ASSIGNED, AssignmentStatus.CONFIRMED, AssignmentStatus.IN_PROGRESS]),
        # Check for date overlap: (start1 <= end2) and (end1 >= start2)
        DriverAssignment.start_date <= end_date,
        DriverAssignment.end_date >= start_date
    )
    
    # Exclude specific assignment if provided
    if exclude_assignment_id:
        query = query.where(DriverAssignment.id != exclude_assignment_id)
    
    conflicts = session.exec(query).all()
    
    return [
        {
            "assignment_id": str(conflict.id),
            "start_date": conflict.start_date,
            "end_date": conflict.end_date,
            "status": conflict.status,
            "tour_title": conflict.tour_title
        }
        for conflict in conflicts
    ]


def validate_training_record(training_data: Dict[str, Any]) -> List[str]:
    """Validate training record data
    
    Args:
        training_data: Training record data
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ['driver_id', 'training_type', 'training_title', 'scheduled_date']
    for field in required_fields:
        if not training_data.get(field):
            errors.append(f"{field} is required")
    
    # Date validation
    if training_data.get('scheduled_date'):
        try:
            scheduled_date = training_data['scheduled_date']
            if isinstance(scheduled_date, str):
                scheduled_date = datetime.strptime(scheduled_date, '%Y-%m-%d').date()
            
            # Training can be scheduled up to 1 year in advance
            max_future_date = date.today() + timedelta(days=365)
            if scheduled_date > max_future_date:
                errors.append("Training cannot be scheduled more than 1 year in advance")
                
        except (ValueError, TypeError):
            errors.append("Invalid scheduled date format")
    
    # Score validation
    if training_data.get('score') is not None:
        score = training_data['score']
        if not isinstance(score, (int, float)) or score < 0 or score > 100:
            errors.append("Score must be between 0 and 100")
    
    # Pass score validation
    if training_data.get('pass_score') is not None:
        pass_score = training_data['pass_score']
        if not isinstance(pass_score, (int, float)) or pass_score < 0 or pass_score > 100:
            errors.append("Pass score must be between 0 and 100")
    
    # Duration validation
    if training_data.get('duration_hours') is not None:
        duration = training_data['duration_hours']
        if not isinstance(duration, (int, float)) or duration <= 0 or duration > 40:
            errors.append("Duration must be between 0 and 40 hours")
    
    return errors


def validate_driver_availability(
    session: Session,
    driver_id: str,
    start_date: date,
    end_date: date
) -> Dict[str, Any]:
    """Validate driver availability for assignment
    
    Args:
        session: Database session
        driver_id: Driver UUID
        start_date: Assignment start date
        end_date: Assignment end date
        
    Returns:
        Availability status and details
    """
    # Get driver
    driver = session.get(Driver, driver_id)
    if not driver:
        return {"available": False, "reason": "Driver not found"}
    
    # Check driver status
    if driver.status != DriverStatus.ACTIVE:
        return {"available": False, "reason": f"Driver status is {driver.status}"}
    
    # Check license expiry
    if driver.license_expiry_date <= start_date:
        return {"available": False, "reason": "Driver license expired"}
    
    # Check health certificate expiry
    if driver.health_certificate_expiry and driver.health_certificate_expiry <= start_date:
        return {"available": False, "reason": "Health certificate expired"}
    
    # Check for conflicts
    conflicts = validate_assignment_conflict(session, driver_id, start_date, end_date)
    if conflicts:
        return {
            "available": False, 
            "reason": "Assignment conflicts exist",
            "conflicts": conflicts
        }
    
    return {"available": True, "reason": "Driver is available"}


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