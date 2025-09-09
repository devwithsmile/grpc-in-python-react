"""
Unit tests for validation utilities.
"""

import pytest
from app.utils.validators import (
    validate_isbn, validate_phone, validate_email_address,
    validate_required_string, validate_positive_integer,
    ValidationError
)


class TestISBNValidation:
    """Test ISBN validation functionality."""
    
    def test_valid_isbn_10(self):
        """Test valid ISBN-10."""
        result = validate_isbn("0-7475-3269-9")
        assert result == "0747532699"
    
    def test_valid_isbn_13(self):
        """Test valid ISBN-13."""
        result = validate_isbn("978-0-7475-3269-9")
        assert result == "9780747532699"
    
    def test_isbn_with_spaces(self):
        """Test ISBN with spaces."""
        result = validate_isbn("978 0 7475 3269 9")
        assert result == "9780747532699"
    
    def test_isbn_10_with_x(self):
        """Test ISBN-10 ending with X."""
        result = validate_isbn("0-201-63361-X")
        assert result == "020163361X"
    
    def test_invalid_isbn_10_check_digit(self):
        """Test invalid ISBN-10 check digit."""
        with pytest.raises(ValidationError) as exc_info:
            validate_isbn("0-7475-3269-0")
        assert "Invalid ISBN-10 check digit" in str(exc_info.value)
        assert exc_info.value.field == "isbn"
    
    def test_invalid_isbn_13_check_digit(self):
        """Test invalid ISBN-13 check digit."""
        with pytest.raises(ValidationError) as exc_info:
            validate_isbn("978-0-7475-3269-0")
        assert "Invalid ISBN-13 check digit" in str(exc_info.value)
        assert exc_info.value.field == "isbn"
    
    def test_invalid_isbn_length(self):
        """Test invalid ISBN length."""
        with pytest.raises(ValidationError) as exc_info:
            validate_isbn("123456789")
        assert "ISBN must be 10 or 13 digits long" in str(exc_info.value)
        assert exc_info.value.field == "isbn"
    
    def test_invalid_isbn_characters(self):
        """Test invalid ISBN characters."""
        with pytest.raises(ValidationError) as exc_info:
            validate_isbn("978-0-7475-3269-A")
        assert "ISBN-13 must contain only digits" in str(exc_info.value)
        assert exc_info.value.field == "isbn"
    
    def test_empty_isbn(self):
        """Test empty ISBN."""
        result = validate_isbn("")
        assert result == ""
    
    def test_none_isbn(self):
        """Test None ISBN."""
        result = validate_isbn(None)
        assert result is None


class TestPhoneValidation:
    """Test phone number validation functionality."""
    
    def test_valid_local_phone(self):
        """Test valid local phone number."""
        result = validate_phone("555-123-4567")
        assert result == "5551234567"
    
    def test_valid_international_phone(self):
        """Test valid international phone number."""
        result = validate_phone("+1-555-123-4567")
        assert result == "+15551234567"
    
    def test_phone_with_spaces(self):
        """Test phone number with spaces."""
        result = validate_phone("+1 555 123 4567")
        assert result == "+15551234567"
    
    def test_phone_with_dots(self):
        """Test phone number with dots."""
        result = validate_phone("555.123.4567")
        assert result == "5551234567"
    
    def test_invalid_local_phone_too_short(self):
        """Test invalid local phone number (too short)."""
        with pytest.raises(ValidationError) as exc_info:
            validate_phone("123")
        assert "Phone number must be 7-15 digits" in str(exc_info.value)
        assert exc_info.value.field == "phone"
    
    def test_invalid_international_phone_too_short(self):
        """Test invalid international phone number (too short)."""
        with pytest.raises(ValidationError) as exc_info:
            validate_phone("+123")
        assert "International phone number must be 8-16 digits" in str(exc_info.value)
        assert exc_info.value.field == "phone"
    
    def test_invalid_international_phone_too_long(self):
        """Test invalid international phone number (too long)."""
        with pytest.raises(ValidationError) as exc_info:
            validate_phone("+12345678901234567")
        assert "International phone number must be 8-16 digits" in str(exc_info.value)
        assert exc_info.value.field == "phone"
    
    def test_empty_phone(self):
        """Test empty phone number."""
        result = validate_phone("")
        assert result == ""
    
    def test_none_phone(self):
        """Test None phone number."""
        result = validate_phone(None)
        assert result is None


class TestEmailValidation:
    """Test email validation functionality."""
    
    def test_valid_email(self):
        """Test valid email address."""
        result = validate_email_address("user@example.com")
        assert result == "user@example.com"
    
    def test_valid_email_with_subdomain(self):
        """Test valid email with subdomain."""
        result = validate_email_address("user@mail.example.com")
        assert result == "user@mail.example.com"
    
    def test_invalid_email_no_at(self):
        """Test invalid email without @."""
        with pytest.raises(ValidationError) as exc_info:
            validate_email_address("userexample.com")
        assert "Invalid email address" in str(exc_info.value)
        assert exc_info.value.field == "email"
    
    def test_invalid_email_no_domain(self):
        """Test invalid email without domain."""
        with pytest.raises(ValidationError) as exc_info:
            validate_email_address("user@")
        assert "Invalid email address" in str(exc_info.value)
        assert exc_info.value.field == "email"
    
    def test_empty_email(self):
        """Test empty email address."""
        with pytest.raises(ValidationError) as exc_info:
            validate_email_address("")
        assert "Email address is required" in str(exc_info.value)
        assert exc_info.value.field == "email"
    
    def test_none_email(self):
        """Test None email address."""
        with pytest.raises(ValidationError) as exc_info:
            validate_email_address(None)
        assert "Email address is required" in str(exc_info.value)
        assert exc_info.value.field == "email"


class TestRequiredStringValidation:
    """Test required string validation functionality."""
    
    def test_valid_string(self):
        """Test valid string."""
        result = validate_required_string("Hello World", "test_field")
        assert result == "Hello World"
    
    def test_string_with_whitespace(self):
        """Test string with whitespace (should be trimmed)."""
        result = validate_required_string("  Hello World  ", "test_field")
        assert result == "Hello World"
    
    def test_empty_string(self):
        """Test empty string."""
        with pytest.raises(ValidationError) as exc_info:
            validate_required_string("", "test_field")
        assert "test_field is required and cannot be empty" in str(exc_info.value)
        assert exc_info.value.field == "test_field"
    
    def test_whitespace_only_string(self):
        """Test whitespace-only string."""
        with pytest.raises(ValidationError) as exc_info:
            validate_required_string("   ", "test_field")
        assert "test_field is required and cannot be empty" in str(exc_info.value)
        assert exc_info.value.field == "test_field"
    
    def test_none_string(self):
        """Test None string."""
        with pytest.raises(ValidationError) as exc_info:
            validate_required_string(None, "test_field")
        assert "test_field is required and cannot be empty" in str(exc_info.value)
        assert exc_info.value.field == "test_field"
    
    def test_string_too_short(self):
        """Test string too short."""
        with pytest.raises(ValidationError) as exc_info:
            validate_required_string("Hi", "test_field", min_length=5)
        assert "test_field must be at least 5 characters long" in str(exc_info.value)
        assert exc_info.value.field == "test_field"
    
    def test_string_too_long(self):
        """Test string too long."""
        with pytest.raises(ValidationError) as exc_info:
            validate_required_string("A" * 300, "test_field", max_length=255)
        assert "test_field must be no more than 255 characters long" in str(exc_info.value)
        assert exc_info.value.field == "test_field"


class TestPositiveIntegerValidation:
    """Test positive integer validation functionality."""
    
    def test_valid_positive_integer(self):
        """Test valid positive integer."""
        result = validate_positive_integer(42, "test_field")
        assert result == 42
    
    def test_zero_integer(self):
        """Test zero integer."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer(0, "test_field")
        assert "test_field must be a positive integer" in str(exc_info.value)
        assert exc_info.value.field == "test_field"
    
    def test_negative_integer(self):
        """Test negative integer."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer(-1, "test_field")
        assert "test_field must be a positive integer" in str(exc_info.value)
        assert exc_info.value.field == "test_field"
    
    def test_string_integer(self):
        """Test string that looks like integer."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer("42", "test_field")
        assert "test_field must be an integer" in str(exc_info.value)
        assert exc_info.value.field == "test_field"
    
    def test_float_integer(self):
        """Test float."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer(42.5, "test_field")
        assert "test_field must be an integer" in str(exc_info.value)
        assert exc_info.value.field == "test_field"
    
    def test_none_integer(self):
        """Test None."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_integer(None, "test_field")
        assert "test_field must be an integer" in str(exc_info.value)
        assert exc_info.value.field == "test_field"
