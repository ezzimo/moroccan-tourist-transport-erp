"""
Data validation utilities for QA service
"""
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
import re
import json
import logging

logger = logging.getLogger(__name__)

# Validation patterns
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PHONE_PATTERN = re.compile(r'^\+?[1-9]\d{1,14}$')  # E.164 format


class ValidationError(Exception):
    """Custom validation error"""
    pass


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


def validate_date_range(start_date: date, end_date: date) -> bool:
    """Validate date range
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        True if valid
    """
    return start_date <= end_date


def validate_score(score: float, min_score: float = 0, max_score: float = 100) -> bool:
    """Validate score range
    
    Args:
        score: Score value
        min_score: Minimum allowed score
        max_score: Maximum allowed score
        
    Returns:
        True if valid
    """
    return min_score <= score <= max_score


def validate_checklist(checklist: Dict[str, Any]) -> List[str]:
    """Validate audit checklist format
    
    Args:
        checklist: Checklist dictionary
        
    Returns:
        List of validation errors
    """
    errors = []
    
    if not isinstance(checklist, dict):
        errors.append("Checklist must be a dictionary")
        return errors
    
    # Required fields
    required_fields = ["items", "total_score"]
    for field in required_fields:
        if field not in checklist:
            errors.append(f"Checklist missing required field: {field}")
    
    # Validate items
    if "items" in checklist:
        items = checklist["items"]
        if not isinstance(items, list):
            errors.append("Checklist items must be a list")
        else:
            for i, item in enumerate(items):
                if not isinstance(item, dict):
                    errors.append(f"Checklist item {i} must be a dictionary")
                    continue
                
                # Required item fields
                item_required = ["question", "score", "max_score"]
                for field in item_required:
                    if field not in item:
                        errors.append(f"Checklist item {i} missing field: {field}")
                
                # Validate scores
                if "score" in item and "max_score" in item:
                    try:
                        score = float(item["score"])
                        max_score = float(item["max_score"])
                        if score > max_score:
                            errors.append(f"Checklist item {i} score exceeds maximum")
                        if score < 0:
                            errors.append(f"Checklist item {i} score cannot be negative")
                    except (ValueError, TypeError):
                        errors.append(f"Checklist item {i} has invalid score values")
    
    # Validate total score
    if "total_score" in checklist:
        try:
            total_score = float(checklist["total_score"])
            if total_score < 0 or total_score > 100:
                errors.append("Total score must be between 0 and 100")
        except (ValueError, TypeError):
            errors.append("Total score must be a number")
    
    return errors


def validate_audit_data(audit_data: Dict[str, Any]) -> List[str]:
    """Validate audit data comprehensively
    
    Args:
        audit_data: Audit data dictionary
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ["entity_type", "entity_id", "scheduled_date"]
    for field in required_fields:
        if not audit_data.get(field):
            errors.append(f"{field} is required")
    
    # Date validation
    if audit_data.get("scheduled_date"):
        try:
            scheduled_date = audit_data["scheduled_date"]
            if isinstance(scheduled_date, str):
                scheduled_date = datetime.strptime(scheduled_date, '%Y-%m-%d').date()
            
            # Audit cannot be scheduled more than 1 year in advance
            max_future_date = date.today() + timedelta(days=365)
            if scheduled_date > max_future_date:
                errors.append("Audit cannot be scheduled more than 1 year in advance")
                
        except (ValueError, TypeError):
            errors.append("Invalid scheduled date format")
    
    # Score validation
    if audit_data.get("score") is not None:
        score = audit_data["score"]
        if not isinstance(score, (int, float)) or not validate_score(score):
            errors.append("Score must be between 0 and 100")
    
    # Entity ID validation
    if audit_data.get("entity_id"):
        try:
            import uuid
            uuid.UUID(str(audit_data["entity_id"]))
        except ValueError:
            errors.append("Invalid entity ID format")
    
    return errors


def validate_compliance_data(compliance_data: Dict[str, Any]) -> List[str]:
    """Validate compliance requirement data
    
    Args:
        compliance_data: Compliance data dictionary
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ["title", "domain", "required_by"]
    for field in required_fields:
        if not compliance_data.get(field):
            errors.append(f"{field} is required")
    
    # Date validation
    if compliance_data.get("next_review_date"):
        try:
            next_review = compliance_data["next_review_date"]
            if isinstance(next_review, str):
                next_review = datetime.strptime(next_review, '%Y-%m-%d').date()
            
            # Review date should be in the future
            if next_review <= date.today():
                errors.append("Next review date should be in the future")
                
        except (ValueError, TypeError):
            errors.append("Invalid next review date format")
    
    # Frequency validation
    if compliance_data.get("frequency_months") is not None:
        frequency = compliance_data["frequency_months"]
        if not isinstance(frequency, int) or frequency <= 0 or frequency > 120:
            errors.append("Frequency must be between 1 and 120 months")
    
    return errors


def validate_certification_data(certification_data: Dict[str, Any]) -> List[str]:
    """Validate certification data
    
    Args:
        certification_data: Certification data dictionary
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ["name", "issuing_body", "entity_type", "entity_id", "issue_date"]
    for field in required_fields:
        if not certification_data.get(field):
            errors.append(f"{field} is required")
    
    # Date validation
    issue_date = certification_data.get("issue_date")
    expiry_date = certification_data.get("expiry_date")
    
    if issue_date:
        try:
            if isinstance(issue_date, str):
                issue_date = datetime.strptime(issue_date, '%Y-%m-%d').date()
            
            # Issue date cannot be more than 10 years in the past
            min_issue_date = date.today() - timedelta(days=10 * 365)
            if issue_date < min_issue_date:
                errors.append("Issue date cannot be more than 10 years in the past")
                
        except (ValueError, TypeError):
            errors.append("Invalid issue date format")
    
    if expiry_date:
        try:
            if isinstance(expiry_date, str):
                expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
            
            if issue_date and expiry_date <= issue_date:
                errors.append("Expiry date must be after issue date")
                
        except (ValueError, TypeError):
            errors.append("Invalid expiry date format")
    
    # Entity ID validation
    if certification_data.get("entity_id"):
        try:
            import uuid
            uuid.UUID(str(certification_data["entity_id"]))
        except ValueError:
            errors.append("Invalid entity ID format")
    
    return errors


def validate_nonconformity_data(nc_data: Dict[str, Any]) -> List[str]:
    """Validate non-conformity data
    
    Args:
        nc_data: Non-conformity data dictionary
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ["description", "severity"]
    for field in required_fields:
        if not nc_data.get(field):
            errors.append(f"{field} is required")
    
    # Description length validation
    if nc_data.get("description"):
        description = nc_data["description"]
        if len(description) < 10:
            errors.append("Description must be at least 10 characters long")
        if len(description) > 2000:
            errors.append("Description cannot exceed 2000 characters")
    
    # Due date validation
    if nc_data.get("due_date"):
        try:
            due_date = nc_data["due_date"]
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            
            # Due date should be in the future
            if due_date <= date.today():
                errors.append("Due date should be in the future")
            
            # Due date should not be more than 1 year in the future
            max_due_date = date.today() + timedelta(days=365)
            if due_date > max_due_date:
                errors.append("Due date cannot be more than 1 year in the future")
                
        except (ValueError, TypeError):
            errors.append("Invalid due date format")
    
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


def validate_json_field(json_str: str, field_name: str) -> Dict[str, Any]:
    """Validate and parse JSON field
    
    Args:
        json_str: JSON string
        field_name: Field name for error messages
        
    Returns:
        Parsed JSON data
        
    Raises:
        ValidationError: If JSON is invalid
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in {field_name}: {str(e)}")


def sanitize_html_input(html_input: str) -> str:
    """Sanitize HTML input to prevent XSS
    
    Args:
        html_input: HTML input string
        
    Returns:
        Sanitized string
    """
    # Basic HTML sanitization - in production, use a proper library like bleach
    import html
    return html.escape(html_input)


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension
    
    Args:
        filename: File name
        allowed_extensions: List of allowed extensions
        
    Returns:
        True if valid
    """
    if not filename:
        return False
    
    file_ext = filename.lower().split('.')[-1]
    return f".{file_ext}" in [ext.lower() for ext in allowed_extensions]