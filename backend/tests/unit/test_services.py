"""
Unit tests for service layer.
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.exc import IntegrityError, OperationalError

from app.services.book_service import BookService
from app.services.member_service import MemberService
from app.services.borrowing_service import BorrowingService
from app.services.validation_service import ValidationService
from app.utils.validators import ValidationError
from app.infrastructure.database import DatabaseError
from app.models.book import Book
from app.models.member import Member
from app.models.borrowing import Borrowing


class TestBookService:
    """Test book service functionality."""
    
    def test_create_book_success(self, mock_get_db_session, mock_validation_service, sample_book_data):
        """Test successful book creation."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_data.return_value = Mock(
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
            isbn="9780743273565"
        )
        mock_book = Mock(spec=Book)
        mock_book.id = 1
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        mock_session.refresh.return_value = None
        
        # Execute
        service = BookService()
        result = service.create_book("The Great Gatsby", "F. Scott Fitzgerald", "978-0743273565")
        
        # Verify
        mock_validation_service.validate_data.assert_called_once()
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()
    
    def test_create_book_validation_error(self, mock_validation_service):
        """Test book creation with validation error."""
        # Setup
        mock_validation_service.validate_data.side_effect = ValidationError("Invalid data", "title", "")
        
        # Execute & Verify
        service = BookService()
        with pytest.raises(ValidationError):
            service.create_book("", "Author", "isbn")
    
    def test_create_book_database_error(self, mock_get_db_session, mock_validation_service):
        """Test book creation with database error."""
        # Setup
        mock_validation_service.validate_data.return_value = Mock(
            title="Test Book",
            author="Test Author",
            isbn="9780743273565"
        )
        mock_get_db_session.side_effect = DatabaseError("Database error", None, "create_book")
        
        # Execute & Verify
        service = BookService()
        with pytest.raises(DatabaseError):
            service.create_book("Test Book", "Test Author", "978-0743273565")
    
    def test_get_book_success(self, mock_get_db_session, mock_validation_service):
        """Test successful book retrieval."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_id.return_value = 1
        mock_book = Mock(spec=Book)
        mock_book.title = "Test Book"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_book
        
        # Execute
        service = BookService()
        result = service.get_book(1)
        
        # Verify
        mock_validation_service.validate_id.assert_called_once_with(1, "Book ID")
        mock_session.query.assert_called_once_with(Book)
        assert result == mock_book
    
    def test_get_book_not_found(self, mock_get_db_session, mock_validation_service):
        """Test book retrieval when book not found."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_id.return_value = 1
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        service = BookService()
        result = service.get_book(1)
        
        # Verify
        assert result is None
    
    def test_get_book_invalid_id(self, mock_validation_service):
        """Test book retrieval with invalid ID."""
        # Setup
        mock_validation_service.validate_id.side_effect = ValidationError("Invalid ID", "id", 0)
        
        # Execute & Verify
        service = BookService()
        with pytest.raises(ValidationError):
            service.get_book(0)
    
    def test_get_all_books_success(self, mock_get_db_session):
        """Test successful retrieval of all books."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_books = [Mock(spec=Book), Mock(spec=Book)]
        mock_session.query.return_value.all.return_value = mock_books
        
        # Execute
        service = BookService()
        result = service.get_all_books()
        
        # Verify
        mock_session.query.assert_called_once_with(Book)
        assert result == mock_books
    
    def test_update_book_success(self, mock_get_db_session, mock_validation_service):
        """Test successful book update."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_id.return_value = 1
        mock_validation_service.validate_data.return_value = Mock(
            title="Updated Title",
            author="Updated Author",
            isbn="9780743273565"
        )
        mock_book = Mock(spec=Book)
        mock_book.title = "Updated Title"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_book
        
        # Execute
        service = BookService()
        result = service.update_book(1, "Updated Title", "Updated Author", "978-0743273565")
        
        # Verify
        mock_validation_service.validate_id.assert_called_once_with(1, "Book ID")
        mock_validation_service.validate_data.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()
    
    def test_update_book_not_found(self, mock_get_db_session, mock_validation_service):
        """Test book update when book not found."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_id.return_value = 1
        mock_validation_service.validate_data.return_value = Mock(
            title="Updated Title",
            author="Updated Author",
            isbn="9780743273565"
        )
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        service = BookService()
        result = service.update_book(1, "Updated Title", "Updated Author", "978-0743273565")
        
        # Verify
        assert result is None
    
    def test_delete_book_success(self, mock_get_db_session, mock_validation_service):
        """Test successful book deletion."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_id.return_value = 1
        mock_book = Mock(spec=Book)
        mock_book.title = "Test Book"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_book
        
        # Execute
        service = BookService()
        result = service.delete_book(1)
        
        # Verify
        mock_validation_service.validate_id.assert_called_once_with(1, "Book ID")
        mock_session.delete.assert_called_once_with(mock_book)
        mock_session.flush.assert_called_once()
        assert result is True
    
    def test_delete_book_not_found(self, mock_get_db_session, mock_validation_service):
        """Test book deletion when book not found."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_id.return_value = 1
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        service = BookService()
        result = service.delete_book(1)
        
        # Verify
        assert result is False


class TestMemberService:
    """Test member service functionality."""
    
    def test_create_member_success(self, mock_get_db_session, mock_validation_service, sample_member_data):
        """Test successful member creation."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_data.return_value = Mock(
            name="John Doe",
            email="john.doe@example.com",
            phone="+15551234567"
        )
        mock_member = Mock(spec=Member)
        mock_member.id = 1
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        mock_session.refresh.return_value = None
        
        # Execute
        service = MemberService()
        result = service.create_member("John Doe", "john.doe@example.com", "+1-555-123-4567")
        
        # Verify
        mock_validation_service.validate_data.assert_called_once()
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()
    
    def test_create_member_validation_error(self, mock_validation_service):
        """Test member creation with validation error."""
        # Setup
        mock_validation_service.validate_data.side_effect = ValidationError("Invalid email", "email", "invalid")
        
        # Execute & Verify
        service = MemberService()
        with pytest.raises(ValidationError):
            service.create_member("John Doe", "invalid-email", "+1-555-123-4567")
    
    def test_get_member_success(self, mock_get_db_session, mock_validation_service):
        """Test successful member retrieval."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_id.return_value = 1
        mock_member = Mock(spec=Member)
        mock_member.name = "John Doe"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_member
        
        # Execute
        service = MemberService()
        result = service.get_member(1)
        
        # Verify
        mock_validation_service.validate_id.assert_called_once_with(1, "Member ID")
        mock_session.query.assert_called_once_with(Member)
        assert result == mock_member


class TestBorrowingService:
    """Test borrowing service functionality."""
    
    def test_borrow_book_success(self, mock_get_db_session, mock_validation_service, sample_borrowing_data):
        """Test successful book borrowing."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_data.return_value = Mock(book_id=1, member_id=1)
        
        # Mock book and member existence
        mock_book = Mock(spec=Book)
        mock_member = Mock(spec=Member)
        mock_session.query.return_value.filter.return_value.first.side_effect = [mock_book, mock_member, None]  # book, member, existing borrowing
        
        mock_borrowing = Mock(spec=Borrowing)
        mock_borrowing.id = 1
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        mock_session.refresh.return_value = None
        
        # Execute
        service = BorrowingService()
        result = service.borrow_book(1, 1)
        
        # Verify
        mock_validation_service.validate_data.assert_called_once()
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()
    
    def test_borrow_book_validation_error(self, mock_validation_service):
        """Test book borrowing with validation error."""
        # Setup
        mock_validation_service.validate_data.side_effect = ValidationError("Invalid ID", "book_id", 0)
        
        # Execute & Verify
        service = BorrowingService()
        with pytest.raises(ValidationError):
            service.borrow_book(0, 1)
    
    def test_borrow_book_not_found(self, mock_get_db_session, mock_validation_service):
        """Test book borrowing when book not found."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_data.return_value = Mock(book_id=1, member_id=1)
        mock_session.query.return_value.filter.return_value.first.return_value = None  # Book not found
        
        # Execute & Verify
        service = BorrowingService()
        with pytest.raises(ValueError, match="Book not found"):
            service.borrow_book(1, 1)
    
    def test_borrow_book_already_borrowed(self, mock_get_db_session, mock_validation_service):
        """Test book borrowing when book is already borrowed."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_data.return_value = Mock(book_id=1, member_id=1)
        
        # Mock book and member existence, but book already borrowed
        mock_book = Mock(spec=Book)
        mock_member = Mock(spec=Member)
        mock_existing_borrowing = Mock(spec=Borrowing)
        mock_session.query.return_value.filter.return_value.first.side_effect = [mock_book, mock_member, mock_existing_borrowing]
        
        # Execute & Verify
        service = BorrowingService()
        with pytest.raises(ValueError, match="Book is already borrowed"):
            service.borrow_book(1, 1)
    
    def test_return_book_success(self, mock_get_db_session, mock_validation_service):
        """Test successful book return."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_data.return_value = Mock(book_id=1, member_id=1)
        
        mock_borrowing = Mock(spec=Borrowing)
        mock_borrowing.id = 1
        mock_session.query.return_value.filter.return_value.first.return_value = mock_borrowing
        mock_session.flush.return_value = None
        mock_session.refresh.return_value = None
        
        # Execute
        service = BorrowingService()
        result = service.return_book(1, 1)
        
        # Verify
        mock_validation_service.validate_data.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()
        assert result == mock_borrowing
    
    def test_return_book_not_found(self, mock_get_db_session, mock_validation_service):
        """Test book return when borrowing not found."""
        # Setup
        mock_session = mock_get_db_session.return_value.__enter__.return_value
        mock_validation_service.validate_data.return_value = Mock(book_id=1, member_id=1)
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Execute & Verify
        service = BorrowingService()
        with pytest.raises(ValueError, match="No active borrowing found"):
            service.return_book(1, 1)


class TestValidationService:
    """Test validation service functionality."""
    
    def test_validate_data_success(self, sample_book_data):
        """Test successful data validation."""
        from app.schemas.book_schemas import BookCreateSchema
        
        service = ValidationService()
        result = service.validate_data(sample_book_data, BookCreateSchema)
        
        assert result.title == sample_book_data["title"]
        assert result.author == sample_book_data["author"]
        assert result.isbn == "9780743273565"  # Cleaned ISBN
    
    def test_validate_data_validation_error(self, invalid_book_data):
        """Test data validation with validation error."""
        from app.schemas.book_schemas import BookCreateSchema
        
        service = ValidationService()
        with pytest.raises(ValidationError):
            service.validate_data(invalid_book_data, BookCreateSchema)
    
    def test_validate_id_success(self):
        """Test successful ID validation."""
        service = ValidationService()
        result = service.validate_id(42, "Test ID")
        assert result == 42
    
    def test_validate_id_invalid(self):
        """Test ID validation with invalid ID."""
        service = ValidationService()
        with pytest.raises(ValidationError):
            service.validate_id(0, "Test ID")
    
    def test_create_validation_error_response(self):
        """Test validation error response creation."""
        service = ValidationService()
        error = ValidationError("Test error", "test_field", "test_value")
        response = service.create_validation_error_response(error, 400)
        
        assert response["error"] == "Validation Error"
        assert response["message"] == "Test error"
        assert response["field"] == "test_field"
        assert response["value"] == "test_value"
        assert response["status_code"] == 400
