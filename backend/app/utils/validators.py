"""
Validation utilities and custom validators for the Library Service.
"""

import re
from typing import Optional, Union
from email_validator import validate_email, EmailNotValidError
from ..utils.logger import LoggerConfig, log_exception


class ValidationError(Exception):
    """Custom validation error with detailed information."""
    
    def __init__(self, message: str, field: str = None, value: str = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)


def validate_isbn(isbn: str) -> str:
    """
    Validate ISBN-10 or ISBN-13 format.
    
    Args:
        isbn: ISBN string to validate
        
    Returns:
        Cleaned ISBN string
        
    Raises:
        ValidationError: If ISBN format is invalid
    """
    if not isbn:
        return isbn
    
    # Remove hyphens and spaces
    cleaned_isbn = re.sub(r'[-\s]', '', isbn)
    
    # Check if it's ISBN-10 (10 digits) or ISBN-13 (13 digits)
    if len(cleaned_isbn) == 10:
        if not cleaned_isbn.isdigit() and not (cleaned_isbn[:-1].isdigit() and cleaned_isbn[-1] in '0123456789X'):
            raise ValidationError(
                "ISBN-10 must contain only digits and optionally end with 'X'",
                field="isbn",
                value=isbn
            )
        
        # Validate ISBN-10 check digit
        if not _validate_isbn10_check_digit(cleaned_isbn):
            raise ValidationError(
                "Invalid ISBN-10 check digit",
                field="isbn",
                value=isbn
            )
            
    elif len(cleaned_isbn) == 13:
        if not cleaned_isbn.isdigit():
            raise ValidationError(
                "ISBN-13 must contain only digits",
                field="isbn",
                value=isbn
            )
        
        # Validate ISBN-13 check digit
        if not _validate_isbn13_check_digit(cleaned_isbn):
            raise ValidationError(
                "Invalid ISBN-13 check digit",
                field="isbn",
                value=isbn
            )
    else:
        raise ValidationError(
            "ISBN must be 10 or 13 digits long",
            field="isbn",
            value=isbn
        )
    
    return cleaned_isbn


def _validate_isbn10_check_digit(isbn: str) -> bool:
    """Validate ISBN-10 check digit."""
    if len(isbn) != 10:
        return False
    
    # Convert last character to number (X = 10)
    last_char = isbn[-1]
    if last_char == 'X':
        check_digit = 10
    else:
        check_digit = int(last_char)
    
    # Calculate check digit
    total = 0
    for i in range(9):
        total += int(isbn[i]) * (10 - i)
    
    return (total + check_digit) % 11 == 0


def _validate_isbn13_check_digit(isbn: str) -> bool:
    """Validate ISBN-13 check digit."""
    if len(isbn) != 13:
        return False
    
    # Calculate check digit
    total = 0
    for i in range(12):
        multiplier = 1 if i % 2 == 0 else 3
        total += int(isbn[i]) * multiplier
    
    check_digit = (10 - (total % 10)) % 10
    return int(isbn[-1]) == check_digit


def validate_phone(phone: str) -> str:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number string to validate
        
    Returns:
        Cleaned phone number string
        
    Raises:
        ValidationError: If phone format is invalid
    """
    if not phone:
        return phone
    
    # Remove all non-digit characters except + at the beginning
    cleaned_phone = re.sub(r'[^\d+]', '', phone)
    
    # Check if it starts with + (international format)
    if cleaned_phone.startswith('+'):
        if len(cleaned_phone) < 8 or len(cleaned_phone) > 16:
            raise ValidationError(
                "International phone number must be 8-16 digits (including country code)",
                field="phone",
                value=phone
            )
    else:
        # Local format - should be 7-15 digits
        if len(cleaned_phone) < 7 or len(cleaned_phone) > 15:
            raise ValidationError(
                "Phone number must be 7-15 digits",
                field="phone",
                value=phone
            )
    
    return cleaned_phone


def validate_email_address(email: str) -> str:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Validated email address
        
    Raises:
        ValidationError: If email format is invalid
    """
    if not email:
        raise ValidationError(
            "Email address is required",
            field="email",
            value=email
        )
    
    try:
        # Validate email format
        validated_email = validate_email(email)
        return validated_email.email
    except EmailNotValidError as e:
        raise ValidationError(
            f"Invalid email address: {str(e)}",
            field="email",
            value=email
        )


def validate_required_string(value: str, field_name: str, min_length: int = 1, max_length: int = 255) -> str:
    """
    Validate required string field.
    
    Args:
        value: String value to validate
        field_name: Name of the field for error messages
        min_length: Minimum length
        max_length: Maximum length
        
    Returns:
        Validated string
        
    Raises:
        ValidationError: If validation fails
    """
    if not value or not value.strip():
        raise ValidationError(
            f"{field_name} is required and cannot be empty",
            field=field_name,
            value=value
        )
    
    value = value.strip()
    
    if len(value) < min_length:
        raise ValidationError(
            f"{field_name} must be at least {min_length} characters long",
            field=field_name,
            value=value
        )
    
    if len(value) > max_length:
        raise ValidationError(
            f"{field_name} must be no more than {max_length} characters long",
            field=field_name,
            value=value
        )
    
    return value


def validate_positive_integer(value: int, field_name: str) -> int:
    """
    Validate positive integer field.
    
    Args:
        value: Integer value to validate
        field_name: Name of the field for error messages
        
    Returns:
        Validated integer
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, int):
        raise ValidationError(
            f"{field_name} must be an integer",
            field=field_name,
            value=value
        )
    
    if value <= 0:
        raise ValidationError(
            f"{field_name} must be a positive integer",
            field=field_name,
            value=value
        )
    
    return value


class ValidationLogger:
    """Logger for validation events."""
    
    def __init__(self):
        self.logger = LoggerConfig.get_logger("validation")
    
    def log_validation_error(self, error: ValidationError, context: dict = None):
        """Log a validation error."""
        log_exception(
            self.logger,
            f"Validation failed: {error.message}",
            error,
            field=error.field,
            value=error.value,
            context=context
        )
    
    def log_validation_success(self, field: str, value: str, context: dict = None):
        """Log successful validation."""
        self.logger.debug(f"Validation successful for {field}: {value}", extra={"context": context})


# Global validation logger instance
validation_logger = ValidationLogger()
