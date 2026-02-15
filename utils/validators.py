"""
Input Validators

Common validation functions for form inputs.
Raises ValidationError on invalid input.
"""
import re
from datetime import datetime


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_email(email):
    """
    Validate email format.
    
    Args:
        email: Email string to validate
        
    Returns:
        str: Normalized email (lowercase, stripped)
        
    Raises:
        ValidationError: If email is invalid
    """
    if not email:
        raise ValidationError("Email is required")
    
    email = email.strip()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format")
    
    return email.lower()


def validate_phone(phone):
    """
    Validate phone number (supports Pakistan format).
    
    Args:
        phone: Phone string to validate
        
    Returns:
        str or None: Normalized phone number
        
    Raises:
        ValidationError: If phone format is invalid
    """
    if not phone:
        return None  # Phone is optional
    
    # Remove spaces, dashes, and parentheses
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Pakistan mobile: 03XX-XXXXXXX or +923XXXXXXXXX
    pattern = r'^(\+92|0)?3[0-9]{9}$'
    
    if not re.match(pattern, phone):
        raise ValidationError("Invalid phone format. Use: 03XX-XXXXXXX")
    
    return phone


def validate_required(value, field_name):
    """
    Validate required field is not empty.
    
    Args:
        value: Value to check
        field_name: Field name for error message
        
    Returns:
        Stripped value if string, original otherwise
        
    Raises:
        ValidationError: If value is empty
    """
    if value is None:
        raise ValidationError(f"{field_name} is required")
    
    if isinstance(value, str):
        value = value.strip()
        if not value:
            raise ValidationError(f"{field_name} is required")
    
    return value


def validate_date(date_string, field_name="Date", required=False):
    """
    Validate date string format.
    
    Args:
        date_string: Date string in YYYY-MM-DD format
        field_name: Field name for error message
        required: Whether field is required
        
    Returns:
        datetime.date or None
        
    Raises:
        ValidationError: If date format is invalid
    """
    if not date_string:
        if required:
            raise ValidationError(f"{field_name} is required")
        return None
    
    try:
        return datetime.strptime(str(date_string).strip(), '%Y-%m-%d').date()
    except ValueError:
        raise ValidationError(f"Invalid {field_name} format. Use YYYY-MM-DD")


def validate_positive_number(value, field_name, allow_zero=False):
    """
    Validate positive numeric value.
    
    Args:
        value: Value to validate
        field_name: Field name for error message
        allow_zero: Whether to allow zero
        
    Returns:
        float: Validated number
        
    Raises:
        ValidationError: If value is not positive
    """
    try:
        num = float(value)
        if allow_zero:
            if num < 0:
                raise ValidationError(f"{field_name} must be zero or positive")
        else:
            if num <= 0:
                raise ValidationError(f"{field_name} must be positive")
        return num
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid number")


def validate_cnic(cnic, required=False):
    """
    Validate Pakistan CNIC format.
    
    Args:
        cnic: CNIC string (13 digits, optionally with dashes)
        required: Whether field is required
        
    Returns:
        str or None: Normalized CNIC (digits only)
        
    Raises:
        ValidationError: If CNIC format is invalid
    """
    if not cnic:
        if required:
            raise ValidationError("CNIC is required")
        return None
    
    # Remove dashes
    cnic = cnic.replace('-', '').strip()
    
    if len(cnic) != 13 or not cnic.isdigit():
        raise ValidationError("CNIC must be 13 digits (e.g., 12345-1234567-1)")
    
    return cnic


def validate_password(password, min_length=8):
    """
    Validate password strength.
    
    Args:
        password: Password string
        min_length: Minimum required length
        
    Returns:
        str: Validated password
        
    Raises:
        ValidationError: If password is too weak
    """
    if not password:
        raise ValidationError("Password is required")
    
    if len(password) < min_length:
        raise ValidationError(f"Password must be at least {min_length} characters")
    
    # Optional: Add complexity requirements
    # if not re.search(r'[A-Z]', password):
    #     raise ValidationError("Password must contain at least one uppercase letter")
    # if not re.search(r'[0-9]', password):
    #     raise ValidationError("Password must contain at least one number")
    
    return password


def sanitize_input(text):
    """
    Sanitize text input to prevent XSS/injection.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return text
    
    if not isinstance(text, str):
        return text
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '\\', '\x00']
    result = text
    for char in dangerous_chars:
        result = result.replace(char, '')
    
    return result.strip()


def validate_name(name, field_name="Name", min_length=2, max_length=100):
    """
    Validate name field.
    
    Args:
        name: Name string
        field_name: Field name for error message
        min_length: Minimum length
        max_length: Maximum length
        
    Returns:
        str: Validated and sanitized name
        
    Raises:
        ValidationError: If name is invalid
    """
    if not name:
        raise ValidationError(f"{field_name} is required")
    
    name = sanitize_input(name.strip())
    
    if len(name) < min_length:
        raise ValidationError(f"{field_name} must be at least {min_length} characters")
    
    if len(name) > max_length:
        raise ValidationError(f"{field_name} must not exceed {max_length} characters")
    
    return name
