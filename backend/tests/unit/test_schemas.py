"""
Unit tests for Pydantic schemas.
"""

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.schemas.book_schemas import BookCreateSchema, BookUpdateSchema, BookResponseSchema
from app.schemas.member_schemas import MemberCreateSchema, MemberUpdateSchema, MemberResponseSchema
from app.schemas.borrowing_schemas import BorrowingCreateSchema, BorrowingReturnSchema, BorrowingResponseSchema


class TestBookSchemas:
    """Test book validation schemas."""
    
    def test_valid_book_create(self):
        """Test valid book creation schema."""
        data = {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "isbn": "978-0743273565"
        }
        book = BookCreateSchema(**data)
        assert book.title == "The Great Gatsby"
        assert book.author == "F. Scott Fitzgerald"
        assert book.isbn == "9780743273565"  # Should be cleaned
    
    def test_book_create_without_isbn(self):
        """Test book creation without ISBN."""
        data = {
            "title": "Test Book",
            "author": "Test Author"
        }
        book = BookCreateSchema(**data)
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.isbn is None
    
    def test_book_create_empty_title(self):
        """Test book creation with empty title."""
        data = {
            "title": "",
            "author": "Test Author"
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            BookCreateSchema(**data)
        assert "String should have at least 1 character" in str(exc_info.value)
    
    def test_book_create_missing_author(self):
        """Test book creation with missing author."""
        data = {
            "title": "Test Book"
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            BookCreateSchema(**data)
        assert "Field required" in str(exc_info.value)
    
    def test_book_create_invalid_isbn(self):
        """Test book creation with invalid ISBN."""
        data = {
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "invalid-isbn"
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            BookCreateSchema(**data)
        assert "ISBN-10 must contain only digits" in str(exc_info.value)
    
    def test_valid_book_update(self):
        """Test valid book update schema."""
        data = {
            "title": "Updated Title",
            "author": "Updated Author",
            "isbn": "978-0743273565"
        }
        book = BookUpdateSchema(**data)
        assert book.title == "Updated Title"
        assert book.author == "Updated Author"
        assert book.isbn == "9780743273565"
    
    def test_book_update_partial(self):
        """Test partial book update."""
        data = {
            "title": "Updated Title"
        }
        book = BookUpdateSchema(**data)
        assert book.title == "Updated Title"
        assert book.author is None
        assert book.isbn is None
    
    def test_book_update_empty(self):
        """Test empty book update."""
        data = {}
        book = BookUpdateSchema(**data)
        assert book.title is None
        assert book.author is None
        assert book.isbn is None
    
    def test_book_response_schema(self):
        """Test book response schema."""
        data = {
            "id": 1,
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "9780743273565",
            "created_at": "2024-01-15T10:30:45Z",
            "updated_at": "2024-01-15T10:30:45Z"
        }
        book = BookResponseSchema(**data)
        assert book.id == 1
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.isbn == "9780743273565"


class TestMemberSchemas:
    """Test member validation schemas."""
    
    def test_valid_member_create(self):
        """Test valid member creation schema."""
        data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-123-4567"
        }
        member = MemberCreateSchema(**data)
        assert member.name == "John Doe"
        assert member.email == "john.doe@example.com"
        assert member.phone == "+15551234567"  # Should be cleaned
    
    def test_member_create_without_phone(self):
        """Test member creation without phone."""
        data = {
            "name": "John Doe",
            "email": "john.doe@example.com"
        }
        member = MemberCreateSchema(**data)
        assert member.name == "John Doe"
        assert member.email == "john.doe@example.com"
        assert member.phone is None
    
    def test_member_create_invalid_email(self):
        """Test member creation with invalid email."""
        data = {
            "name": "John Doe",
            "email": "invalid-email"
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            MemberCreateSchema(**data)
        assert "Invalid email address" in str(exc_info.value)
    
    def test_member_create_empty_name(self):
        """Test member creation with empty name."""
        data = {
            "name": "",
            "email": "john@example.com"
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            MemberCreateSchema(**data)
        assert "String should have at least 1 character" in str(exc_info.value)
    
    def test_member_create_missing_email(self):
        """Test member creation with missing email."""
        data = {
            "name": "John Doe"
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            MemberCreateSchema(**data)
        assert "Field required" in str(exc_info.value)
    
    def test_member_create_invalid_phone(self):
        """Test member creation with invalid phone."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "123"  # Too short
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            MemberCreateSchema(**data)
        assert "Phone number must be 7-15 digits" in str(exc_info.value)
    
    def test_valid_member_update(self):
        """Test valid member update schema."""
        data = {
            "name": "Updated Name",
            "email": "updated@example.com",
            "phone": "+1-555-987-6543"
        }
        member = MemberUpdateSchema(**data)
        assert member.name == "Updated Name"
        assert member.email == "updated@example.com"
        assert member.phone == "+15559876543"
    
    def test_member_update_partial(self):
        """Test partial member update."""
        data = {
            "name": "Updated Name"
        }
        member = MemberUpdateSchema(**data)
        assert member.name == "Updated Name"
        assert member.email is None
        assert member.phone is None
    
    def test_member_response_schema(self):
        """Test member response schema."""
        data = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+15551234567",
            "created_at": "2024-01-15T10:30:45Z",
            "updated_at": "2024-01-15T10:30:45Z"
        }
        member = MemberResponseSchema(**data)
        assert member.id == 1
        assert member.name == "John Doe"
        assert member.email == "john@example.com"
        assert member.phone == "+15551234567"


class TestBorrowingSchemas:
    """Test borrowing validation schemas."""
    
    def test_valid_borrowing_create(self):
        """Test valid borrowing creation schema."""
        data = {
            "book_id": 1,
            "member_id": 1
        }
        borrowing = BorrowingCreateSchema(**data)
        assert borrowing.book_id == 1
        assert borrowing.member_id == 1
    
    def test_borrowing_create_invalid_book_id(self):
        """Test borrowing creation with invalid book ID."""
        data = {
            "book_id": 0,  # Must be positive
            "member_id": 1
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            BorrowingCreateSchema(**data)
        assert "Input should be greater than 0" in str(exc_info.value)
    
    def test_borrowing_create_invalid_member_id(self):
        """Test borrowing creation with invalid member ID."""
        data = {
            "book_id": 1,
            "member_id": -1  # Must be positive
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            BorrowingCreateSchema(**data)
        assert "Input should be greater than 0" in str(exc_info.value)
    
    def test_borrowing_create_missing_book_id(self):
        """Test borrowing creation with missing book ID."""
        data = {
            "member_id": 1
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            BorrowingCreateSchema(**data)
        assert "Field required" in str(exc_info.value)
    
    def test_borrowing_create_missing_member_id(self):
        """Test borrowing creation with missing member ID."""
        data = {
            "book_id": 1
        }
        with pytest.raises(PydanticValidationError) as exc_info:
            BorrowingCreateSchema(**data)
        assert "Field required" in str(exc_info.value)
    
    def test_valid_borrowing_return(self):
        """Test valid borrowing return schema."""
        data = {
            "book_id": 1,
            "member_id": 1
        }
        borrowing = BorrowingReturnSchema(**data)
        assert borrowing.book_id == 1
        assert borrowing.member_id == 1
    
    def test_borrowing_response_schema(self):
        """Test borrowing response schema."""
        data = {
            "id": 1,
            "book_id": 1,
            "member_id": 1,
            "borrow_date": "2024-01-15T10:30:45Z",
            "return_date": None,
            "is_returned": False
        }
        borrowing = BorrowingResponseSchema(**data)
        assert borrowing.id == 1
        assert borrowing.book_id == 1
        assert borrowing.member_id == 1
        assert borrowing.borrow_date == "2024-01-15T10:30:45Z"
        assert borrowing.return_date is None
        assert borrowing.is_returned is False
