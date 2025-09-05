"""
Currency utilities for safe monetary calculations
"""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Union, Optional
import logging

logger = logging.getLogger(__name__)

# Supported currencies with their decimal places
SUPPORTED_CURRENCIES = {
    'MAD': 2,  # Moroccan Dirham
    'EUR': 2,  # Euro
    'USD': 2,  # US Dollar
    'GBP': 2,  # British Pound
}

DEFAULT_CURRENCY = 'MAD'


def safe_decimal(value: Union[str, int, float, Decimal, None], default: Decimal = Decimal('0')) -> Decimal:
    """
    Safely convert a value to Decimal
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Decimal value or default
    """
    if value is None or value == '':
        return default
    
    try:
        if isinstance(value, Decimal):
            return value
        
        # Convert to string first to handle various input types
        str_value = str(value).strip()
        
        if not str_value:
            return default
        
        decimal_value = Decimal(str_value)
        
        # Check for reasonable bounds
        if decimal_value < Decimal('-999999999'):
            logger.warning(f"Value {value} is too small, using default")
            return default
        
        if decimal_value > Decimal('999999999'):
            logger.warning(f"Value {value} is too large, using default")
            return default
        
        return decimal_value
        
    except (InvalidOperation, ValueError, TypeError) as e:
        logger.warning(f"Failed to convert {value} to Decimal: {e}")
        return default


def validate_currency_amount(amount: Union[str, int, float, Decimal], currency: str = DEFAULT_CURRENCY) -> Decimal:
    """
    Validate and format a currency amount
    
    Args:
        amount: Amount to validate
        currency: Currency code
        
    Returns:
        Validated and formatted Decimal amount
        
    Raises:
        ValueError: If amount is invalid
    """
    if currency not in SUPPORTED_CURRENCIES:
        raise ValueError(f"Unsupported currency: {currency}")
    
    decimal_amount = safe_decimal(amount)
    
    if decimal_amount < 0:
        raise ValueError("Amount cannot be negative")
    
    # Get decimal places for currency
    decimal_places = SUPPORTED_CURRENCIES[currency]
    
    # Quantize to appropriate decimal places
    quantize_value = Decimal('0.1') ** decimal_places
    return decimal_amount.quantize(quantize_value, rounding=ROUND_HALF_UP)


def format_currency(amount: Union[str, int, float, Decimal], currency: str = DEFAULT_CURRENCY) -> str:
    """
    Format an amount as currency string
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    try:
        decimal_amount = validate_currency_amount(amount, currency)
        
        if currency == 'MAD':
            return f"{decimal_amount:,.2f} MAD"
        elif currency == 'EUR':
            return f"€{decimal_amount:,.2f}"
        elif currency == 'USD':
            return f"${decimal_amount:,.2f}"
        elif currency == 'GBP':
            return f"£{decimal_amount:,.2f}"
        else:
            return f"{decimal_amount:,.2f} {currency}"
            
    except Exception as e:
        logger.warning(f"Error formatting currency {amount} {currency}: {e}")
        return f"0.00 {currency}"


def add_currency_amounts(*amounts: Union[str, int, float, Decimal]) -> Decimal:
    """
    Safely add multiple currency amounts
    
    Args:
        amounts: Variable number of amounts to add
        
    Returns:
        Sum as Decimal
    """
    total = Decimal('0')
    
    for amount in amounts:
        safe_amount = safe_decimal(amount)
        total += safe_amount
    
    return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def multiply_currency(amount: Union[str, int, float, Decimal], multiplier: Union[str, int, float, Decimal]) -> Decimal:
    """
    Safely multiply a currency amount
    
    Args:
        amount: Amount to multiply
        multiplier: Multiplier value
        
    Returns:
        Result as Decimal
    """
    safe_amount = safe_decimal(amount)
    safe_multiplier = safe_decimal(multiplier, Decimal('1'))
    
    result = safe_amount * safe_multiplier
    return result.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_percentage(amount: Union[str, int, float, Decimal], percentage: Union[str, int, float, Decimal]) -> Decimal:
    """
    Calculate percentage of an amount
    
    Args:
        amount: Base amount
        percentage: Percentage (e.g., 10 for 10%)
        
    Returns:
        Percentage amount as Decimal
    """
    safe_amount = safe_decimal(amount)
    safe_percentage = safe_decimal(percentage)
    
    if safe_percentage < 0 or safe_percentage > 100:
        logger.warning(f"Invalid percentage: {percentage}")
        return Decimal('0')
    
    result = safe_amount * (safe_percentage / Decimal('100'))
    return result.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)