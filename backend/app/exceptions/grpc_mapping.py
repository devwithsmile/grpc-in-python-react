"""
gRPC status code mapping for Library Service exceptions.
"""

import grpc
from typing import Tuple, Optional
from .base import LibraryServiceError, ErrorCode


class GRPCStatusMapper:
    """Maps Library Service exceptions to gRPC status codes."""
    
    # Mapping from ErrorCode to gRPC StatusCode
    ERROR_CODE_TO_GRPC_STATUS = {
        # Validation errors
        ErrorCode.VALIDATION_ERROR: grpc.StatusCode.INVALID_ARGUMENT,
        ErrorCode.REQUIRED_FIELD_MISSING: grpc.StatusCode.INVALID_ARGUMENT,
        ErrorCode.INVALID_FORMAT: grpc.StatusCode.INVALID_ARGUMENT,
        ErrorCode.INVALID_LENGTH: grpc.StatusCode.INVALID_ARGUMENT,
        ErrorCode.INVALID_VALUE: grpc.StatusCode.INVALID_ARGUMENT,
        
        # Business logic errors
        ErrorCode.RESOURCE_NOT_FOUND: grpc.StatusCode.NOT_FOUND,
        ErrorCode.RESOURCE_ALREADY_EXISTS: grpc.StatusCode.ALREADY_EXISTS,
        ErrorCode.BUSINESS_RULE_VIOLATION: grpc.StatusCode.FAILED_PRECONDITION,
        ErrorCode.OPERATION_NOT_ALLOWED: grpc.StatusCode.FAILED_PRECONDITION,
        ErrorCode.CONFLICT: grpc.StatusCode.ABORTED,
        
        # Database errors
        ErrorCode.DATABASE_ERROR: grpc.StatusCode.INTERNAL,
        ErrorCode.INTEGRITY_CONSTRAINT_VIOLATION: grpc.StatusCode.INTERNAL,
        ErrorCode.CONNECTION_ERROR: grpc.StatusCode.UNAVAILABLE,
        ErrorCode.TRANSACTION_ERROR: grpc.StatusCode.INTERNAL,
        
        # Authentication/Authorization errors
        ErrorCode.UNAUTHORIZED: grpc.StatusCode.UNAUTHENTICATED,
        ErrorCode.FORBIDDEN: grpc.StatusCode.PERMISSION_DENIED,
        ErrorCode.INVALID_CREDENTIALS: grpc.StatusCode.UNAUTHENTICATED,
        
        # System errors
        ErrorCode.INTERNAL_ERROR: grpc.StatusCode.INTERNAL,
        ErrorCode.SERVICE_UNAVAILABLE: grpc.StatusCode.UNAVAILABLE,
        ErrorCode.TIMEOUT: grpc.StatusCode.DEADLINE_EXCEEDED,
        ErrorCode.RATE_LIMIT_EXCEEDED: grpc.StatusCode.RESOURCE_EXHAUSTED,
    }
    
    @classmethod
    def map_exception_to_grpc_status(
        cls, 
        exception: LibraryServiceError
    ) -> Tuple[grpc.StatusCode, str]:
        """
        Map a Library Service exception to gRPC status code and details.
        
        Args:
            exception: The Library Service exception to map
            
        Returns:
            Tuple of (grpc_status_code, details_string)
        """
        # Get the gRPC status code
        grpc_status = cls.ERROR_CODE_TO_GRPC_STATUS.get(
            exception.error_code, 
            grpc.StatusCode.INTERNAL
        )
        
        # Build details string
        details_parts = [exception.message]
        
        if exception.field:
            details_parts.append(f"Field: {exception.field}")
        
        if exception.details:
            for key, value in exception.details.items():
                details_parts.append(f"{key}: {value}")
        
        details = " | ".join(details_parts)
        
        return grpc_status, details
    
    @classmethod
    def map_generic_exception_to_grpc_status(
        cls, 
        exception: Exception
    ) -> Tuple[grpc.StatusCode, str]:
        """
        Map a generic exception to gRPC status code and details.
        
        Args:
            exception: The generic exception to map
            
        Returns:
            Tuple of (grpc_status_code, details_string)
        """
        # Map common exception types
        if isinstance(exception, ValueError):
            return grpc.StatusCode.INVALID_ARGUMENT, str(exception)
        elif isinstance(exception, KeyError):
            return grpc.StatusCode.INVALID_ARGUMENT, f"Missing required field: {str(exception)}"
        elif isinstance(exception, TypeError):
            return grpc.StatusCode.INVALID_ARGUMENT, f"Invalid type: {str(exception)}"
        elif isinstance(exception, AttributeError):
            return grpc.StatusCode.INVALID_ARGUMENT, f"Invalid attribute: {str(exception)}"
        else:
            return grpc.StatusCode.INTERNAL, f"Internal error: {str(exception)}"
    
    @classmethod
    def get_grpc_status_for_error_code(cls, error_code: ErrorCode) -> grpc.StatusCode:
        """
        Get gRPC status code for a specific error code.
        
        Args:
            error_code: The error code to map
            
        Returns:
            gRPC status code
        """
        return cls.ERROR_CODE_TO_GRPC_STATUS.get(error_code, grpc.StatusCode.INTERNAL)
    
    @classmethod
    def is_retryable_error(cls, exception: LibraryServiceError) -> bool:
        """
        Check if an error is retryable based on the gRPC status code.
        
        Args:
            exception: The Library Service exception to check
            
        Returns:
            True if the error is retryable, False otherwise
        """
        grpc_status, _ = cls.map_exception_to_grpc_status(exception)
        
        # Retryable status codes
        retryable_statuses = {
            grpc.StatusCode.UNAVAILABLE,
            grpc.StatusCode.DEADLINE_EXCEEDED,
            grpc.StatusCode.RESOURCE_EXHAUSTED,
            grpc.StatusCode.ABORTED,  # Can be retryable for transient conflicts
        }
        
        return grpc_status in retryable_statuses
    
    @classmethod
    def get_error_category(cls, exception: LibraryServiceError) -> str:
        """
        Get the error category for an exception.
        
        Args:
            exception: The Library Service exception to categorize
            
        Returns:
            Error category string
        """
        error_code = exception.error_code
        
        if error_code in {
            ErrorCode.VALIDATION_ERROR,
            ErrorCode.REQUIRED_FIELD_MISSING,
            ErrorCode.INVALID_FORMAT,
            ErrorCode.INVALID_LENGTH,
            ErrorCode.INVALID_VALUE
        }:
            return "validation"
        elif error_code in {
            ErrorCode.RESOURCE_NOT_FOUND,
            ErrorCode.RESOURCE_ALREADY_EXISTS,
            ErrorCode.BUSINESS_RULE_VIOLATION,
            ErrorCode.OPERATION_NOT_ALLOWED,
            ErrorCode.CONFLICT
        }:
            return "business_logic"
        elif error_code in {
            ErrorCode.DATABASE_ERROR,
            ErrorCode.INTEGRITY_CONSTRAINT_VIOLATION,
            ErrorCode.CONNECTION_ERROR,
            ErrorCode.TRANSACTION_ERROR
        }:
            return "database"
        elif error_code in {
            ErrorCode.UNAUTHORIZED,
            ErrorCode.FORBIDDEN,
            ErrorCode.INVALID_CREDENTIALS
        }:
            return "authorization"
        else:
            return "system"
