"""
Base exception classes for the Library Service.
"""

from typing import Optional, Dict, Any
from enum import Enum


class ErrorCode(Enum):
    """Error codes for different types of errors."""
    
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"
    INVALID_FORMAT = "INVALID_FORMAT"
    INVALID_LENGTH = "INVALID_LENGTH"
    INVALID_VALUE = "INVALID_VALUE"
    
    # Business logic errors
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    CONFLICT = "CONFLICT"
    
    # Database errors
    DATABASE_ERROR = "DATABASE_ERROR"
    INTEGRITY_CONSTRAINT_VIOLATION = "INTEGRITY_CONSTRAINT_VIOLATION"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    TRANSACTION_ERROR = "TRANSACTION_ERROR"
    
    # Authentication/Authorization errors
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    
    # System errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    TIMEOUT = "TIMEOUT"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"


class LibraryServiceError(Exception):
    """Base exception class for all Library Service errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None,
        field: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.field = field
        self.original_error = original_error
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        result = {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code.value,
            "details": self.details
        }
        
        if self.field:
            result["field"] = self.field
        
        if self.original_error:
            result["original_error"] = str(self.original_error)
        
        return result
    
    def __str__(self) -> str:
        """String representation of the exception."""
        base_msg = f"{self.__class__.__name__}: {self.message}"
        if self.field:
            base_msg += f" (field: {self.field})"
        if self.details:
            base_msg += f" (details: {self.details})"
        return base_msg


class ValidationError(LibraryServiceError):
    """Exception raised for validation errors."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_code = ErrorCode.VALIDATION_ERROR
        if field and not value:
            error_code = ErrorCode.REQUIRED_FIELD_MISSING
        elif "format" in message.lower():
            error_code = ErrorCode.INVALID_FORMAT
        elif "length" in message.lower():
            error_code = ErrorCode.INVALID_LENGTH
        elif "invalid" in message.lower():
            error_code = ErrorCode.INVALID_VALUE
        
        validation_details = details or {}
        if value is not None:
            validation_details["value"] = value
        
        super().__init__(
            message=message,
            error_code=error_code,
            details=validation_details,
            field=field
        )


class BusinessLogicError(LibraryServiceError):
    """Exception raised for business logic errors."""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.BUSINESS_RULE_VIOLATION,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details
        )


class ResourceNotFoundError(BusinessLogicError):
    """Exception raised when a resource is not found."""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: Any,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(
            message=message,
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            details=details or {"resource_type": resource_type, "resource_id": resource_id}
        )


class ResourceAlreadyExistsError(BusinessLogicError):
    """Exception raised when a resource already exists."""
    
    def __init__(
        self,
        resource_type: str,
        identifier: str,
        value: Any,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource_type} with {identifier} '{value}' already exists"
        super().__init__(
            message=message,
            error_code=ErrorCode.RESOURCE_ALREADY_EXISTS,
            details=details or {"resource_type": resource_type, "identifier": identifier, "value": value}
        )


class ConflictError(BusinessLogicError):
    """Exception raised when there's a conflict in business logic."""
    
    def __init__(
        self,
        message: str,
        conflicting_resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.CONFLICT,
            details=details or {"conflicting_resource": conflicting_resource}
        )


class OperationNotAllowedError(BusinessLogicError):
    """Exception raised when an operation is not allowed."""
    
    def __init__(
        self,
        operation: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Operation '{operation}' is not allowed: {reason}"
        super().__init__(
            message=message,
            error_code=ErrorCode.OPERATION_NOT_ALLOWED,
            details=details or {"operation": operation, "reason": reason}
        )


class DatabaseError(LibraryServiceError):
    """Exception raised for database errors."""
    
    def __init__(
        self,
        message: str,
        operation: str,
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_code = ErrorCode.DATABASE_ERROR
        if original_error:
            error_name = original_error.__class__.__name__
            if "IntegrityError" in error_name:
                error_code = ErrorCode.INTEGRITY_CONSTRAINT_VIOLATION
            elif "OperationalError" in error_name:
                error_code = ErrorCode.CONNECTION_ERROR
        
        super().__init__(
            message=message,
            error_code=error_code,
            details=details or {"operation": operation},
            original_error=original_error
        )


class ServiceError(LibraryServiceError):
    """Exception raised for service-level errors."""
    
    def __init__(
        self,
        message: str,
        service_name: str,
        error_code: ErrorCode = ErrorCode.SERVICE_UNAVAILABLE,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details or {"service_name": service_name}
        )
