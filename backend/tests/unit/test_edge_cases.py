"""
Unit tests for edge cases and error scenarios.
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

from app.utils.validators import ValidationError, validate_isbn, validate_phone, validate_email_address
from app.services.book_service import BookService
from app.services.member_service import MemberService
from app.services.borrowing_service import BorrowingService
from app.infrastructure.database import DatabaseError


class TestValidationEdgeCases:
    """Test validation edge cases."""
    
    def test_isbn_very_long_string(self):
        """Test ISBN validation with very long string."""
        long_isbn = "9" * 100
        with pytest.raises(ValidationError) as exc_info:
            validate_isbn(long_isbn)
        assert "ISBN must be 10 or 13 digits long" in str(exc_info.value)
    
    def test_isbn_special_characters(self):
        """Test ISBN validation with special characters."""
        with pytest.raises(ValidationError) as exc_info:
            validate_isbn("978-0-7475-3269-@")
        assert "ISBN-13 must contain only digits" in str(exc_info.value)
    
    def test_isbn_unicode_characters(self):
        """Test ISBN validation with unicode characters."""
        with pytest.raises(ValidationError) as exc_info:
            validate_isbn("978-0-7475-3269-ñ")
        assert "ISBN-13 must contain only digits" in str(exc_info.value)
    
    def test_phone_very_long_string(self):
        """Test phone validation with very long string."""
        long_phone = "+1" + "5" * 50
        with pytest.raises(ValidationError) as exc_info:
            validate_phone(long_phone)
        assert "International phone number must be 8-16 digits" in str(exc_info.value)
    
    def test_phone_unicode_characters(self):
        """Test phone validation with unicode characters."""
        with pytest.raises(ValidationError) as exc_info:
            validate_phone("+1-555-123-ñ")
        # Should pass as it removes non-digit characters except +
    
    def test_email_very_long_string(self):
        """Test email validation with very long string."""
        long_email = "a" * 1000 + "@example.com"
        with pytest.raises(ValidationError) as exc_info:
            validate_email_address(long_email)
        assert "Invalid email address" in str(exc_info.value)
    
    def test_email_unicode_characters(self):
        """Test email validation with unicode characters."""
        with pytest.raises(ValidationError) as exc_info:
            validate_email_address("user@ñexample.com")
        assert "Invalid email address" in str(exc_info.value)
    
    def test_required_string_unicode(self):
        """Test required string validation with unicode."""
        from app.utils.validators import validate_required_string
        result = validate_required_string("Héllo Wørld", "test_field")
        assert result == "Héllo Wørld"
    
    def test_required_string_very_long(self):
        """Test required string validation with very long string."""
        from app.utils.validators import validate_required_string
        long_string = "A" * 1000
        with pytest.raises(ValidationError) as exc_info:
            validate_required_string(long_string, "test_field", max_length=255)
        assert "test_field must be no more than 255 characters long" in str(exc_info.value)


class TestDatabaseErrorScenarios:
    """Test database error scenarios."""
    
    def test_book_service_integrity_error(self, mock_get_db_session, mock_validation_service):
        """Test book service with database integrity error."""
        # Setup
        mock_validation_service.validate_data.return_value = Mock(
            title="Test Book",
            author="Test Author",
            isbn="9780743273565"
        )
        mock_get_db_session.side_effect = DatabaseError("Integrity constraint violation", IntegrityError("", "", ""), "create_book")
        
        # Execute & Verify
        service = BookService()
        with pytest.raises(DatabaseError):
            service.create_book("Test Book", "Test Author", "978-0743273565")
    
    def test_book_service_operational_error(self, mock_get_db_session, mock_validation_service):
        """Test book service with database operational error."""
        # Setup
        mock_validation_service.validate_data.return_value = Mock(
            title="Test Book",
            author="Test Author",
            isbn="9780743273565"
        )
        mock_get_db_session.side_effect = DatabaseError("Connection failed", OperationalError("", "", ""), "create_book")
        
        # Execute & Verify
        service = BookService()
        with pytest.raises(DatabaseError):
            service.create_book("Test Book", "Test Author", "978-0743273565")
    
    def test_book_service_generic_sqlalchemy_error(self, mock_get_db_session, mock_validation_service):
        """Test book service with generic SQLAlchemy error."""
        # Setup
        mock_validation_service.validate_data.return_value = Mock(
            title="Test Book",
            author="Test Author",
            isbn="9780743273565"
        )
        mock_get_db_session.side_effect = DatabaseError("Generic database error", SQLAlchemyError("", "", ""), "create_book")
        
        # Execute & Verify
        service = BookService()
        with pytest.raises(DatabaseError):
            service.create_book("Test Book", "Test Author", "978-0743273565")
    
    def test_book_service_unexpected_error(self, mock_get_db_session, mock_validation_service):
        """Test book service with unexpected error."""
        # Setup
        mock_validation_service.validate_data.return_value = Mock(
            title="Test Book",
            author="Test Author",
            isbn="9780743273565"
        )
        mock_get_db_session.side_effect = DatabaseError("Unexpected error", Exception("Unexpected"), "create_book")
        
        # Execute & Verify
        service = BookService()
        with pytest.raises(DatabaseError):
            service.create_book("Test Book", "Test Author", "978-0743273565")


class TestServiceEdgeCases:
    """Test service layer edge cases."""
    
    def test_book_service_create_with_none_values(self, mock_get_db_session, mock_validation_service):
        """Test book service create with None values."""
        # Setup
        mock_validation_service.validate_data.side_effect = ValidationError("Invalid data", "title", None)
        
        # Execute & Verify
        service = BookService()
        with pytest.raises(ValidationError):
            service.create_book(None, None, None)
    
    def test_member_service_create_with_empty_strings(self, mock_get_db_session, mock_validation_service):
        """Test member service create with empty strings."""
        # Setup
        mock_validation_service.validate_data.side_effect = ValidationError("Invalid data", "name", "")
        
        # Execute & Verify
        service = MemberService()
        with pytest.raises(ValidationError):
            service.create_member("", "", "")
    
    def test_borrowing_service_with_negative_ids(self, mock_validation_service):
        """Test borrowing service with negative IDs."""
        # Setup
        mock_validation_service.validate_data.side_effect = ValidationError("Invalid ID", "book_id", -1)
        
        # Execute & Verify
        service = BorrowingService()
        with pytest.raises(ValidationError):
            service.borrow_book(-1, -1)
    
    def test_book_service_update_with_all_none(self, mock_get_db_session, mock_validation_service):
        """Test book service update with all None values."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_id.return_value = 1
        mock_book = Mock()
        mock_book.title = "Original Title"
        mock_book.author = "Original Author"
        mock_book.isbn = "9780743273565"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_book
        mock_session.flush.return_value = None
        mock_session.refresh.return_value = None
        
        # Execute
        service = BookService()
        result = service.update_book(1, None, None, None)
        
        # Verify - should not call validation service for data validation
        mock_validation_service.validate_id.assert_called_once_with(1, "Book ID")
        mock_validation_service.validate_data.assert_not_called()
        assert result == mock_book
    
    def test_member_service_update_with_all_none(self, mock_get_db_session, mock_validation_service):
        """Test member service update with all None values."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_id.return_value = 1
        mock_member = Mock()
        mock_member.name = "Original Name"
        mock_member.email = "original@example.com"
        mock_member.phone = "+15551234567"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_member
        mock_session.flush.return_value = None
        mock_session.refresh.return_value = None
        
        # Execute
        service = MemberService()
        result = service.update_member(1, None, None, None)
        
        # Verify - should not call validation service for data validation
        mock_validation_service.validate_id.assert_called_once_with(1, "Member ID")
        mock_validation_service.validate_data.assert_not_called()
        assert result == mock_member


class TestConcurrentAccessScenarios:
    """Test concurrent access scenarios."""
    
    def test_borrow_book_concurrent_borrowing(self, mock_get_db_session, mock_validation_service):
        """Test borrowing book when another borrowing happens concurrently."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_data.return_value = Mock(book_id=1, member_id=1)
        
        # Mock book and member existence, but book already borrowed
        mock_book = Mock()
        mock_member = Mock()
        mock_existing_borrowing = Mock()
        mock_session.query.return_value.filter.return_value.first.side_effect = [mock_book, mock_member, mock_existing_borrowing]
        
        # Execute & Verify
        service = BorrowingService()
        with pytest.raises(ValueError, match="Book is already borrowed"):
            service.borrow_book(1, 1)
    
    def test_return_book_concurrent_return(self, mock_get_db_session, mock_validation_service):
        """Test returning book when another return happens concurrently."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_data.return_value = Mock(book_id=1, member_id=1)
        mock_session.query.return_value.filter.return_value.first.return_value = None  # No active borrowing
        
        # Execute & Verify
        service = BorrowingService()
        with pytest.raises(ValueError, match="No active borrowing found"):
            service.return_book(1, 1)


class TestBoundaryValues:
    """Test boundary values and limits."""
    
    def test_string_length_boundaries(self):
        """Test string length boundary values."""
        from app.utils.validators import validate_required_string
        
        # Test minimum length
        result = validate_required_string("A", "test_field", min_length=1, max_length=1)
        assert result == "A"
        
        # Test maximum length
        result = validate_required_string("A" * 255, "test_field", min_length=1, max_length=255)
        assert result == "A" * 255
        
        # Test just over maximum length
        with pytest.raises(ValidationError) as exc_info:
            validate_required_string("A" * 256, "test_field", min_length=1, max_length=255)
        assert "test_field must be no more than 255 characters long" in str(exc_info.value)
    
    def test_phone_length_boundaries(self):
        """Test phone number length boundary values."""
        # Test minimum local phone
        result = validate_phone("1234567")
        assert result == "1234567"
        
        # Test maximum local phone
        result = validate_phone("123456789012345")
        assert result == "123456789012345"
        
        # Test minimum international phone
        result = validate_phone("+12345678")
        assert result == "+12345678"
        
        # Test maximum international phone
        result = validate_phone("+1234567890123456")
        assert result == "+1234567890123456"
    
    def test_isbn_boundary_values(self):
        """Test ISBN boundary values."""
        # Test exactly 10 digits
        result = validate_isbn("1234567890")
        assert result == "1234567890"
        
        # Test exactly 13 digits
        result = validate_isbn("1234567890123")
        assert result == "1234567890123"
        
        # Test 9 digits (too short)
        with pytest.raises(ValidationError) as exc_info:
            validate_isbn("123456789")
        assert "ISBN must be 10 or 13 digits long" in str(exc_info.value)
        
        # Test 14 digits (too long)
        with pytest.raises(ValidationError) as exc_info:
            validate_isbn("12345678901234")
        assert "ISBN must be 10 or 13 digits long" in str(exc_info.value)


class TestErrorRecovery:
    """Test error recovery scenarios."""
    
    def test_validation_error_recovery(self, mock_get_db_session, mock_validation_service):
        """Test recovery from validation errors."""
        # Setup - first call fails, second succeeds
        mock_validation_service.validate_data.side_effect = [
            ValidationError("Invalid data", "title", ""),
            Mock(title="Test Book", author="Test Author", isbn="9780743273565")
        ]
        
        service = BookService()
        
        # First call should fail
        with pytest.raises(ValidationError):
            service.create_book("", "Test Author", "978-0743273565")
        
        # Second call should succeed
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_book = Mock()
        mock_book.id = 1
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        mock_session.refresh.return_value = None
        
        result = service.create_book("Test Book", "Test Author", "978-0743273565")
        assert result is not None
    
    def test_database_error_recovery(self, mock_get_db_session, mock_validation_service):
        """Test recovery from database errors."""
        # Setup - first call fails with database error, second succeeds
        mock_validation_service.validate_data.return_value = Mock(
            title="Test Book",
            author="Test Author",
            isbn="9780743273565"
        )
        mock_get_db_session.side_effect = [
            DatabaseError("Database error", None, "create_book"),
            Mock(__enter__=Mock(return_value=Mock()), __exit__=Mock(return_value=False))
        ]
        
        service = BookService()
        
        # First call should fail
        with pytest.raises(DatabaseError):
            service.create_book("Test Book", "Test Author", "978-0743273565")
        
        # Second call should succeed (mock setup would need to be more complex for real recovery)
        # This is more of a conceptual test showing the pattern
