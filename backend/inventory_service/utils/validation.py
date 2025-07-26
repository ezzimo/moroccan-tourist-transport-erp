"""
Data validation utilities for inventory service
"""
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal
from models.item import Item, ItemCategory
from models.stock_movement import MovementType
import re
import logging

logger = logging.getLogger(__name__)

# Validation patterns
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PHONE_PATTERN = re.compile(r'^\+?[1-9]\d{1,14}$')  # E.164 format
MOROCCO_PHONE_PATTERN = re.compile(r'^\+212[5-7]\d{8}$|^0[5-7]\d{8}$')


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


def validate_phone_number(phone: str, morocco_only: bool = True) -> bool:
    """Validate phone number format
    
    Args:
        phone: Phone number string
        morocco_only: If True, validates Morocco-specific format
        
    Returns:
        True if valid
    """
    if not phone:
        return False
    
    # Remove spaces and dashes
    clean_phone = re.sub(r'[\s-]', '', phone)
    
    if morocco_only:
        return bool(MOROCCO_PHONE_PATTERN.match(clean_phone))
    else:
        return bool(PHONE_PATTERN.match(clean_phone))


def validate_positive_number(value: Any, field_name: str) -> List[str]:
    """Validate positive number
    
    Args:
        value: Value to validate
        field_name: Field name for error messages
        
    Returns:
        List of validation errors
    """
    errors = []
    
    if value is None:
        errors.append(f"{field_name} is required")
        return errors
    
    try:
        num_value = float(value)
        if num_value < 0:
            errors.append(f"{field_name} must be positive")
        if num_value == 0 and field_name.lower() in ['quantity', 'unit_cost', 'price']:
            errors.append(f"{field_name} must be greater than zero")
    except (ValueError, TypeError):
        errors.append(f"{field_name} must be a valid number")
    
    return errors


def validate_item_data(item_data: Dict[str, Any]) -> List[str]:
    """Validate item data comprehensively
    
    Args:
        item_data: Item data dictionary
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ['name', 'unit', 'unit_cost', 'reorder_level']
    for field in required_fields:
        if not item_data.get(field):
            errors.append(f"{field} is required")
    
    # Name validation
    name = item_data.get('name', '')
    if name and len(name.strip()) < 2:
        errors.append("Item name must be at least 2 characters long")
    if name and len(name) > 255:
        errors.append("Item name must not exceed 255 characters")
    
    # Unit cost validation
    errors.extend(validate_positive_number(item_data.get('unit_cost'), 'unit_cost'))
    
    # Quantity validation
    current_quantity = item_data.get('current_quantity', 0)
    if current_quantity is not None:
        try:
            qty = int(current_quantity)
            if qty < 0:
                errors.append("Current quantity cannot be negative")
        except (ValueError, TypeError):
            errors.append("Current quantity must be a valid integer")
    
    # Reorder level validation
    reorder_level = item_data.get('reorder_level')
    if reorder_level is not None:
        try:
            reorder = int(reorder_level)
            if reorder < 0:
                errors.append("Reorder level cannot be negative")
        except (ValueError, TypeError):
            errors.append("Reorder level must be a valid integer")
    
    # Category validation
    category = item_data.get('category')
    if category:
        try:
            ItemCategory(category)
        except ValueError:
            valid_categories = [cat.value for cat in ItemCategory]
            errors.append(f"Invalid category. Valid options: {', '.join(valid_categories)}")
    
    # Unit validation
    unit = item_data.get('unit', '')
    if unit and len(unit.strip()) < 1:
        errors.append("Unit is required")
    if unit and len(unit) > 50:
        errors.append("Unit must not exceed 50 characters")
    
    # Warehouse location validation
    warehouse_location = item_data.get('warehouse_location', '')
    if warehouse_location and len(warehouse_location) > 100:
        errors.append("Warehouse location must not exceed 100 characters")
    
    return errors


def validate_stock_movement(movement_data: Dict[str, Any], item: Optional[Item] = None) -> List[str]:
    """Validate stock movement data
    
    Args:
        movement_data: Movement data dictionary
        item: Item being moved (for additional validation)
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ['item_id', 'type', 'quantity']
    for field in required_fields:
        if not movement_data.get(field):
            errors.append(f"{field} is required")
    
    # Movement type validation
    movement_type = movement_data.get('type')
    if movement_type:
        try:
            MovementType(movement_type)
        except ValueError:
            valid_types = [mt.value for mt in MovementType]
            errors.append(f"Invalid movement type. Valid options: {', '.join(valid_types)}")
    
    # Quantity validation
    quantity = movement_data.get('quantity')
    if quantity is not None:
        try:
            qty = int(quantity)
            if qty <= 0:
                errors.append("Quantity must be greater than zero")
            
            # Additional validation for OUT movements
            if movement_type == MovementType.OUT and item:
                if qty > item.current_quantity:
                    errors.append(f"Cannot move {qty} items. Only {item.current_quantity} available in stock")
                    
        except (ValueError, TypeError):
            errors.append("Quantity must be a valid positive integer")
    
    # Reference validation
    reference = movement_data.get('reference', '')
    if reference and len(reference) > 255:
        errors.append("Reference must not exceed 255 characters")
    
    # Notes validation
    notes = movement_data.get('notes', '')
    if notes and len(notes) > 1000:
        errors.append("Notes must not exceed 1000 characters")
    
    return errors


def validate_supplier_data(supplier_data: Dict[str, Any]) -> List[str]:
    """Validate supplier data
    
    Args:
        supplier_data: Supplier data dictionary
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ['name', 'contact_person']
    for field in required_fields:
        if not supplier_data.get(field):
            errors.append(f"{field} is required")
    
    # Name validation
    name = supplier_data.get('name', '')
    if name and len(name.strip()) < 2:
        errors.append("Supplier name must be at least 2 characters long")
    if name and len(name) > 255:
        errors.append("Supplier name must not exceed 255 characters")
    
    # Contact person validation
    contact_person = supplier_data.get('contact_person', '')
    if contact_person and len(contact_person.strip()) < 2:
        errors.append("Contact person name must be at least 2 characters long")
    if contact_person and len(contact_person) > 255:
        errors.append("Contact person name must not exceed 255 characters")
    
    # Email validation
    email = supplier_data.get('email')
    if email and not validate_email(email):
        errors.append("Invalid email format")
    
    # Phone validation
    phone = supplier_data.get('phone')
    if phone and not validate_phone_number(phone):
        errors.append("Invalid Morocco phone number format")
    
    # Address validation
    address = supplier_data.get('address', '')
    if address and len(address) > 500:
        errors.append("Address must not exceed 500 characters")
    
    # Payment terms validation
    payment_terms = supplier_data.get('payment_terms', '')
    if payment_terms and len(payment_terms) > 255:
        errors.append("Payment terms must not exceed 255 characters")
    
    # Average delivery time validation
    delivery_time = supplier_data.get('average_delivery_time')
    if delivery_time is not None:
        try:
            days = int(delivery_time)
            if days < 0:
                errors.append("Average delivery time cannot be negative")
            if days > 365:
                errors.append("Average delivery time cannot exceed 365 days")
        except (ValueError, TypeError):
            errors.append("Average delivery time must be a valid number of days")
    
    # Performance score validation
    performance_score = supplier_data.get('performance_score')
    if performance_score is not None:
        try:
            score = float(performance_score)
            if not (0 <= score <= 100):
                errors.append("Performance score must be between 0 and 100")
        except (ValueError, TypeError):
            errors.append("Performance score must be a valid number")
    
    return errors


def validate_purchase_order(order_data: Dict[str, Any]) -> List[str]:
    """Validate purchase order data
    
    Args:
        order_data: Purchase order data dictionary
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ['supplier_id', 'items']
    for field in required_fields:
        if not order_data.get(field):
            errors.append(f"{field} is required")
    
    # Items validation
    items = order_data.get('items', [])
    if not items:
        errors.append("At least one item is required")
    elif not isinstance(items, list):
        errors.append("Items must be a list")
    else:
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"Item {i+1} must be an object")
                continue
            
            # Required item fields
            if not item.get('item_id'):
                errors.append(f"Item {i+1}: item_id is required")
            
            if not item.get('quantity'):
                errors.append(f"Item {i+1}: quantity is required")
            else:
                try:
                    qty = int(item['quantity'])
                    if qty <= 0:
                        errors.append(f"Item {i+1}: quantity must be greater than zero")
                except (ValueError, TypeError):
                    errors.append(f"Item {i+1}: quantity must be a valid integer")
            
            # Unit price validation (optional, will use item's unit cost if not provided)
            unit_price = item.get('unit_price')
            if unit_price is not None:
                try:
                    price = Decimal(str(unit_price))
                    if price < 0:
                        errors.append(f"Item {i+1}: unit price cannot be negative")
                except (ValueError, TypeError):
                    errors.append(f"Item {i+1}: unit price must be a valid number")
    
    # Notes validation
    notes = order_data.get('notes', '')
    if notes and len(notes) > 1000:
        errors.append("Notes must not exceed 1000 characters")
    
    return errors


def validate_date_range(start_date: Optional[date], end_date: Optional[date]) -> List[str]:
    """Validate date range
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        List of validation errors
    """
    errors = []
    
    if start_date and end_date:
        if start_date > end_date:
            errors.append("Start date must be before or equal to end date")
        
        # Check if date range is reasonable (not more than 5 years)
        if (end_date - start_date).days > 1825:  # 5 years
            errors.append("Date range cannot exceed 5 years")
    
    # Check if dates are not too far in the future
    if start_date and start_date > date.today() + timedelta(days=365):
        errors.append("Start date cannot be more than 1 year in the future")
    
    if end_date and end_date > date.today() + timedelta(days=365):
        errors.append("End date cannot be more than 1 year in the future")
    
    return errors


def validate_warehouse_location(location: str, valid_locations: Optional[List[str]] = None) -> List[str]:
    """Validate warehouse location
    
    Args:
        location: Warehouse location
        valid_locations: List of valid locations (if None, any non-empty string is valid)
        
    Returns:
        List of validation errors
    """
    errors = []
    
    if not location or not location.strip():
        errors.append("Warehouse location is required")
        return errors
    
    if len(location) > 100:
        errors.append("Warehouse location must not exceed 100 characters")
    
    if valid_locations and location not in valid_locations:
        errors.append(f"Invalid warehouse location. Valid options: {', '.join(valid_locations)}")
    
    return errors


def validate_currency_code(currency: str) -> List[str]:
    """Validate currency code
    
    Args:
        currency: Currency code (e.g., MAD, USD, EUR)
        
    Returns:
        List of validation errors
    """
    errors = []
    
    if not currency:
        errors.append("Currency code is required")
        return errors
    
    # Common currency codes for Morocco and international trade
    valid_currencies = ['MAD', 'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF']
    
    if currency.upper() not in valid_currencies:
        errors.append(f"Invalid currency code. Valid options: {', '.join(valid_currencies)}")
    
    if len(currency) != 3:
        errors.append("Currency code must be exactly 3 characters")
    
    return errors


def raise_validation_error(errors: List[str]) -> None:
    """Raise HTTP exception for validation errors
    
    Args:
        errors: List of validation error messages
    """
    if errors:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Validation failed",
                "errors": errors
            }
        )