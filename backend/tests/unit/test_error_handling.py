"""
Unit tests for error handling system.
"""

import pytest
import grpc
from unittest.mock import Mock, patch

from app.exceptions.base import (
    LibraryServiceError, ValidationError, BusinessLogicError,
    ResourceNotFoundError, ResourceAlreadyExistsError, ConflictError,
    OperationNotAllowedError, DatabaseError, ServiceError, ErrorCode
)
from app.exceptions.library_exceptions import (
    BookNotFoundError, BookAlreadyExistsError, MemberNotFoundError,
    BookAlreadyBorrowedError, BookNotBorrowedError, BookNotAvailableError
)
from app.exceptions.grpc_mapping import GRPCStatusMapper
from app.exceptions.error_handler import ErrorHandler


class TestLibraryServiceError:
    """Test base LibraryServiceError class."""
    
    def test_error_creation(self):
        """Test error creation with all parameters."""
        error = LibraryServiceError(
            message="Test error",
            error_code=ErrorCode.VALIDATION_ERROR,
            details={"field": "test_field", "value": "test_value"},
            field="test_field",
            original_error=ValueError("Original error")
        )
        
        assert error.message == "Test error"
        assert error.error_code == ErrorCode.VALIDATION_ERROR
        assert error.details == {"field": "test_field", "value": "test_value"}
        assert error.field == "test_field"
        assert error.original_error is not None
    
    def test_error_to_dict(self):
        """Test error serialization to dictionary."""
        error = LibraryServiceError(
            message="Test error",
            error_code=ErrorCode.VALIDATION_ERROR,
            details={"field": "test_field"},
            field="test_field",
            original_error=ValueError("Original error")
        )
        
        error_dict = error.to_dict()
        
        assert error_dict["error"] == "LibraryServiceError"
        assert error_dict["message"] == "Test error"
        assert error_dict["error_code"] == "VALIDATION_ERROR"
        assert error_dict["details"] == {"field": "test_field"}
        assert error_dict["field"] == "test_field"
        assert error_dict["original_error"] == "Original error"
    
    def test_error_str_representation(self):
        """Test string representation of error."""
        error = LibraryServiceError(
            message="Test error",
            error_code=ErrorCode.VALIDATION_ERROR,
            field="test_field",
            details={"key": "value"}
        )
        
        error_str = str(error)
        assert "LibraryServiceError: Test error" in error_str
        assert "field: test_field" in error_str
        assert "details: {'key': 'value'}" in error_str


class TestValidationError:
    """Test ValidationError class."""
    
    def test_validation_error_creation(self):
        """Test validation error creation."""
        error = ValidationError(
            message="Invalid format",
            field="email",
            value="invalid-email"
        )
        
        assert error.message == "Invalid format"
        assert error.field == "email"
        assert error.details["value"] == "invalid-email"
        assert error.error_code == ErrorCode.INVALID_FORMAT
    
    def test_validation_error_required_field(self):
        """Test validation error for required field."""
        error = ValidationError(
            message="Field is required",
            field="title"
        )
        
        assert error.error_code == ErrorCode.REQUIRED_FIELD_MISSING
    
    def test_validation_error_invalid_length(self):
        """Test validation error for invalid length."""
        error = ValidationError(
            message="String too long",
            field="description"
        )
        
        assert error.error_code == ErrorCode.INVALID_LENGTH


class TestBusinessLogicErrors:
    """Test business logic error classes."""
    
    def test_resource_not_found_error(self):
        """Test ResourceNotFoundError."""
        error = ResourceNotFoundError("Book", 123)
        
        assert error.message == "Book with ID 123 not found"
        assert error.error_code == ErrorCode.RESOURCE_NOT_FOUND
        assert error.details["resource_type"] == "Book"
        assert error.details["resource_id"] == 123
    
    def test_resource_already_exists_error(self):
        """Test ResourceAlreadyExistsError."""
        error = ResourceAlreadyExistsError("Book", "ISBN", "978-1234567890")
        
        assert error.message == "Book with ISBN '978-1234567890' already exists"
        assert error.error_code == ErrorCode.RESOURCE_ALREADY_EXISTS
        assert error.details["resource_type"] == "Book"
        assert error.details["identifier"] == "ISBN"
        assert error.details["value"] == "978-1234567890"
    
    def test_conflict_error(self):
        """Test ConflictError."""
        error = ConflictError("Resource is locked", "user_123")
        
        assert error.message == "Resource is locked"
        assert error.error_code == ErrorCode.CONFLICT
        assert error.details["conflicting_resource"] == "user_123"
    
    def test_operation_not_allowed_error(self):
        """Test OperationNotAllowedError."""
        error = OperationNotAllowedError("delete_book", "Book has active borrowings")
        
        assert error.message == "Operation 'delete_book' is not allowed: Book has active borrowings"
        assert error.error_code == ErrorCode.OPERATION_NOT_ALLOWED
        assert error.details["operation"] == "delete_book"
        assert error.details["reason"] == "Book has active borrowings"


class TestLibrarySpecificErrors:
    """Test library-specific error classes."""
    
    def test_book_not_found_error(self):
        """Test BookNotFoundError."""
        error = BookNotFoundError(123)
        
        assert error.message == "Book with ID 123 not found"
        assert error.error_code == ErrorCode.RESOURCE_NOT_FOUND
        assert error.details["book_id"] == 123
        assert error.details["resource_type"] == "Book"
    
    def test_book_already_exists_error(self):
        """Test BookAlreadyExistsError."""
        error = BookAlreadyExistsError("978-1234567890")
        
        assert error.message == "Book with ISBN 978-1234567890 already exists"
        assert error.error_code == ErrorCode.RESOURCE_ALREADY_EXISTS
        assert error.details["isbn"] == "978-1234567890"
        assert error.details["resource_type"] == "Book"
    
    def test_book_already_borrowed_error(self):
        """Test BookAlreadyBorrowedError."""
        error = BookAlreadyBorrowedError(123, 456)
        
        assert error.message == "Book with ID 123 is already borrowed by member 456"
        assert error.error_code == ErrorCode.CONFLICT
        assert error.details["book_id"] == 123
        assert error.details["current_borrower_id"] == 456
        assert error.details["conflict_type"] == "book_already_borrowed"
    
    def test_book_not_borrowed_error(self):
        """Test BookNotBorrowedError."""
        error = BookNotBorrowedError(123, 456)
        
        assert error.message == "Operation 'return_book' is not allowed: Book 123 is not currently borrowed by member 456"
        assert error.error_code == ErrorCode.OPERATION_NOT_ALLOWED
        assert error.details["book_id"] == 123
        assert error.details["member_id"] == 456
        assert error.details["operation"] == "return_book"


class TestGRPCStatusMapper:
    """Test gRPC status code mapping."""
    
    def test_validation_error_mapping(self):
        """Test mapping of validation errors to gRPC status codes."""
        error = ValidationError("Invalid format", "email")
        grpc_status, details = GRPCStatusMapper.map_exception_to_grpc_status(error)
        
        assert grpc_status == grpc.StatusCode.INVALID_ARGUMENT
        assert "Invalid format" in details
        assert "Field: email" in details
    
    def test_resource_not_found_mapping(self):
        """Test mapping of resource not found errors."""
        error = BookNotFoundError(123)
        grpc_status, details = GRPCStatusMapper.map_exception_to_grpc_status(error)
        
        assert grpc_status == grpc.StatusCode.NOT_FOUND
        assert "Book with ID 123 not found" in details
    
    def test_conflict_mapping(self):
        """Test mapping of conflict errors."""
        error = BookAlreadyBorrowedError(123, 456)
        grpc_status, details = GRPCStatusMapper.map_exception_to_grpc_status(error)
        
        assert grpc_status == grpc.StatusCode.ABORTED
        assert "Book with ID 123 is already borrowed" in details
    
    def test_database_error_mapping(self):
        """Test mapping of database errors."""
        error = DatabaseError("Connection failed", "create_book")
        grpc_status, details = GRPCStatusMapper.map_exception_to_grpc_status(error)
        
        assert grpc_status == grpc.StatusCode.INTERNAL
        assert "Connection failed" in details
    
    def test_generic_exception_mapping(self):
        """Test mapping of generic exceptions."""
        error = ValueError("Invalid value")
        grpc_status, details = GRPCStatusMapper.map_generic_exception_to_grpc_status(error)
        
        assert grpc_status == grpc.StatusCode.INVALID_ARGUMENT
        assert "Invalid value" in details
    
    def test_retryable_error_detection(self):
        """Test retryable error detection."""
        # Non-retryable error
        error = ValidationError("Invalid format", "email")
        assert not GRPCStatusMapper.is_retryable_error(error)
        
        # Retryable error
        error = DatabaseError("Connection failed", "create_book")
        error.error_code = ErrorCode.CONNECTION_ERROR
        assert GRPCStatusMapper.is_retryable_error(error)
    
    def test_error_category_detection(self):
        """Test error category detection."""
        # Validation error
        error = ValidationError("Invalid format", "email")
        assert GRPCStatusMapper.get_error_category(error) == "validation"
        
        # Business logic error
        error = BookNotFoundError(123)
        assert GRPCStatusMapper.get_error_category(error) == "business_logic"
        
        # Database error
        error = DatabaseError("Connection failed", "create_book")
        assert GRPCStatusMapper.get_error_category(error) == "database"


class TestErrorHandler:
    """Test ErrorHandler class."""
    
    def test_handle_library_service_error(self):
        """Test handling of LibraryServiceError."""
        handler = ErrorHandler("test_handler")
        error = ValidationError("Invalid format", "email")
        
        transformed_error, log_data = handler.handle_exception(
            error,
            context={"test": "data"},
            operation="test_operation"
        )
        
        assert transformed_error == error
        assert log_data["exception_type"] == "ValidationError"
        assert log_data["operation"] == "test_operation"
        assert log_data["error_code"] == "INVALID_FORMAT"
        assert log_data["error_category"] == "validation"
    
    def test_handle_generic_exception(self):
        """Test handling of generic exceptions."""
        handler = ErrorHandler("test_handler")
        error = ValueError("Test error")
        
        transformed_error, log_data = handler.handle_exception(
            error,
            context={"test": "data"},
            operation="test_operation"
        )
        
        assert isinstance(transformed_error, LibraryServiceError)
        assert transformed_error.error_code == ErrorCode.INTERNAL_ERROR
        assert log_data["error_code"] == "INTERNAL_ERROR"
        assert log_data["error_category"] == "system"
    
    def test_handle_grpc_exception(self):
        """Test handling of gRPC exceptions."""
        handler = ErrorHandler("test_handler")
        error = BookNotFoundError(123)
        
        transformed_error, grpc_status, details = handler.handle_grpc_exception(
            error,
            context={"book_id": 123},
            operation="GetBook"
        )
        
        assert transformed_error == error
        assert grpc_status == grpc.StatusCode.NOT_FOUND
        assert "Book with ID 123 not found" in details
    
    def test_handle_rest_exception(self):
        """Test handling of REST exceptions."""
        handler = ErrorHandler("test_handler")
        error = ValidationError("Invalid format", "email")
        
        transformed_error, http_status, response = handler.handle_rest_exception(
            error,
            context={"email": "invalid"},
            operation="create_member"
        )
        
        assert transformed_error == error
        assert http_status == 400
        assert response["error"] == "ValidationError"
        assert response["message"] == "Invalid format"
        assert response["status_code"] == 400
    
    def test_error_handler_context_manager(self):
        """Test error handler context manager."""
        handler = ErrorHandler("test_handler")
        
        with handler.handle_errors("test_operation", {"test": "data"}) as h:
            # Should not raise an exception
            pass
        
        # Test with exception
        with pytest.raises(ValueError):
            with handler.handle_errors("test_operation", {"test": "data"}) as h:
                raise ValueError("Test error")


class TestErrorHandlingIntegration:
    """Test error handling integration scenarios."""
    
    def test_validation_error_flow(self):
        """Test complete validation error flow."""
        # Create validation error
        error = ValidationError("Invalid email format", "email", "invalid-email")
        
        # Map to gRPC
        grpc_status, grpc_details = GRPCStatusMapper.map_exception_to_grpc_status(error)
        assert grpc_status == grpc.StatusCode.INVALID_ARGUMENT
        assert "Invalid email format" in grpc_details
        
        # Map to REST
        handler = ErrorHandler("test_handler")
        _, http_status, response = handler.handle_rest_exception(error, operation="create_member")
        assert http_status == 400
        assert response["error_code"] == "INVALID_FORMAT"
    
    def test_business_logic_error_flow(self):
        """Test complete business logic error flow."""
        # Create business logic error
        error = BookNotFoundError(123)
        
        # Map to gRPC
        grpc_status, grpc_details = GRPCStatusMapper.map_exception_to_grpc_status(error)
        assert grpc_status == grpc.StatusCode.NOT_FOUND
        assert "Book with ID 123 not found" in grpc_details
        
        # Map to REST
        handler = ErrorHandler("test_handler")
        _, http_status, response = handler.handle_rest_exception(error, operation="get_book")
        assert http_status == 404
        assert response["error_code"] == "RESOURCE_NOT_FOUND"
    
    def test_database_error_flow(self):
        """Test complete database error flow."""
        # Create database error
        error = DatabaseError("Connection failed", "create_book")
        
        # Map to gRPC
        grpc_status, grpc_details = GRPCStatusMapper.map_exception_to_grpc_status(error)
        assert grpc_status == grpc.StatusCode.INTERNAL
        assert "Connection failed" in grpc_details
        
        # Map to REST
        handler = ErrorHandler("test_handler")
        _, http_status, response = handler.handle_rest_exception(error, operation="create_book")
        assert http_status == 500
        assert response["error_code"] == "DATABASE_ERROR"
