"""
Error handling utilities with structured logging.
"""

import logging
from typing import Optional, Dict, Any, Tuple
from contextlib import contextmanager
import traceback

from .base import LibraryServiceError, ErrorCode
from .grpc_mapping import GRPCStatusMapper
from ..utils.logger import LoggerConfig, log_exception


class ErrorHandler:
    """Centralized error handling with structured logging."""
    
    def __init__(self, logger_name: str = "error_handler"):
        self.logger = LoggerConfig.get_logger(logger_name)
    
    def handle_exception(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        operation: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Tuple[LibraryServiceError, Dict[str, Any]]:
        """
        Handle an exception with structured logging and error transformation.
        
        Args:
            exception: The exception to handle
            context: Additional context information
            operation: The operation that failed
            user_id: User ID for audit logging
            request_id: Request ID for tracing
            
        Returns:
            Tuple of (transformed_exception, log_data)
        """
        # Build log data
        log_data = {
            "exception_type": exception.__class__.__name__,
            "exception_message": str(exception),
            "operation": operation,
            "user_id": user_id,
            "request_id": request_id,
            "context": context or {}
        }
        
        # Transform exception if needed
        if isinstance(exception, LibraryServiceError):
            transformed_exception = exception
            log_data["error_code"] = exception.error_code.value
            log_data["error_category"] = GRPCStatusMapper.get_error_category(exception)
        else:
            # Transform generic exception to LibraryServiceError
            transformed_exception = LibraryServiceError(
                message=f"Unexpected error: {str(exception)}",
                error_code=ErrorCode.INTERNAL_ERROR,
                original_error=exception,
                details={"original_type": exception.__class__.__name__}
            )
            log_data["error_code"] = ErrorCode.INTERNAL_ERROR.value
            log_data["error_category"] = "system"
        
        # Add stack trace for debugging
        log_data["stack_trace"] = traceback.format_exc()
        
        # Log the error
        self._log_error(transformed_exception, log_data)
        
        return transformed_exception, log_data
    
    def _log_error(self, exception: LibraryServiceError, log_data: Dict[str, Any]):
        """Log the error with appropriate level based on error type."""
        error_code = exception.error_code
        
        # Determine log level based on error type
        if error_code in {
            ErrorCode.INTERNAL_ERROR,
            ErrorCode.DATABASE_ERROR,
            ErrorCode.CONNECTION_ERROR,
            ErrorCode.SERVICE_UNAVAILABLE
        }:
            log_level = logging.ERROR
        elif error_code in {
            ErrorCode.BUSINESS_RULE_VIOLATION,
            ErrorCode.OPERATION_NOT_ALLOWED,
            ErrorCode.CONFLICT,
            ErrorCode.INTEGRITY_CONSTRAINT_VIOLATION
        }:
            log_level = logging.WARNING
        elif error_code in {
            ErrorCode.VALIDATION_ERROR,
            ErrorCode.REQUIRED_FIELD_MISSING,
            ErrorCode.INVALID_FORMAT,
            ErrorCode.INVALID_LENGTH,
            ErrorCode.INVALID_VALUE
        }:
            log_level = logging.INFO
        else:
            log_level = logging.WARNING
        
        # Log with structured data
        self.logger.log(
            log_level,
            f"Error in {log_data.get('operation', 'unknown')}: {exception.message}",
            extra=log_data
        )
    
    def handle_grpc_exception(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        operation: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Tuple[LibraryServiceError, int, str]:
        """
        Handle an exception for gRPC with status code mapping.
        
        Args:
            exception: The exception to handle
            context: Additional context information
            operation: The operation that failed
            user_id: User ID for audit logging
            request_id: Request ID for tracing
            
        Returns:
            Tuple of (transformed_exception, grpc_status_code, details_string)
        """
        # Handle the exception
        transformed_exception, log_data = self.handle_exception(
            exception, context, operation, user_id, request_id
        )
        
        # Map to gRPC status
        grpc_status, details = GRPCStatusMapper.map_exception_to_grpc_status(transformed_exception)
        
        # Log gRPC-specific information
        self.logger.info(
            f"gRPC error response: {grpc_status.name} - {details}",
            extra={
                "grpc_status": grpc_status.name,
                "grpc_code": grpc_status.value,
                "details": details,
                **log_data
            }
        )
        
        return transformed_exception, grpc_status, details
    
    def handle_rest_exception(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        operation: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Tuple[LibraryServiceError, int, Dict[str, Any]]:
        """
        Handle an exception for REST API with HTTP status code mapping.
        
        Args:
            exception: The exception to handle
            context: Additional context information
            operation: The operation that failed
            user_id: User ID for audit logging
            request_id: Request ID for tracing
            
        Returns:
            Tuple of (transformed_exception, http_status_code, response_dict)
        """
        # Handle the exception
        transformed_exception, log_data = self.handle_exception(
            exception, context, operation, user_id, request_id
        )
        
        # Map to HTTP status code
        http_status = self._map_to_http_status(transformed_exception)
        
        # Build response dictionary
        response_dict = transformed_exception.to_dict()
        response_dict["status_code"] = http_status
        
        # Log REST-specific information
        self.logger.info(
            f"REST error response: {http_status} - {transformed_exception.message}",
            extra={
                "http_status": http_status,
                "response": response_dict,
                **log_data
            }
        )
        
        return transformed_exception, http_status, response_dict
    
    def _map_to_http_status(self, exception: LibraryServiceError) -> int:
        """Map Library Service exception to HTTP status code."""
        error_code = exception.error_code
        
        # Mapping from ErrorCode to HTTP status code
        error_code_to_http_status = {
            # Validation errors -> 400 Bad Request
            ErrorCode.VALIDATION_ERROR: 400,
            ErrorCode.REQUIRED_FIELD_MISSING: 400,
            ErrorCode.INVALID_FORMAT: 400,
            ErrorCode.INVALID_LENGTH: 400,
            ErrorCode.INVALID_VALUE: 400,
            
            # Business logic errors
            ErrorCode.RESOURCE_NOT_FOUND: 404,
            ErrorCode.RESOURCE_ALREADY_EXISTS: 409,
            ErrorCode.BUSINESS_RULE_VIOLATION: 422,
            ErrorCode.OPERATION_NOT_ALLOWED: 403,
            ErrorCode.CONFLICT: 409,
            
            # Database errors -> 500 Internal Server Error
            ErrorCode.DATABASE_ERROR: 500,
            ErrorCode.INTEGRITY_CONSTRAINT_VIOLATION: 500,
            ErrorCode.CONNECTION_ERROR: 503,
            ErrorCode.TRANSACTION_ERROR: 500,
            
            # Authentication/Authorization errors
            ErrorCode.UNAUTHORIZED: 401,
            ErrorCode.FORBIDDEN: 403,
            ErrorCode.INVALID_CREDENTIALS: 401,
            
            # System errors
            ErrorCode.INTERNAL_ERROR: 500,
            ErrorCode.SERVICE_UNAVAILABLE: 503,
            ErrorCode.TIMEOUT: 504,
            ErrorCode.RATE_LIMIT_EXCEEDED: 429,
        }
        
        return error_code_to_http_status.get(error_code, 500)
    
    @contextmanager
    def handle_errors(
        self,
        operation: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """
        Context manager for error handling.
        
        Usage:
            with error_handler.handle_errors("create_book", {"book_id": 1}) as handler:
                # Your code here
                pass
        """
        try:
            yield self
        except Exception as e:
            self.handle_exception(e, context, operation, user_id, request_id)
            raise


# Global error handler instance
error_handler = ErrorHandler()


def handle_exception_with_logging(
    exception: Exception,
    logger: logging.Logger,
    operation: str,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None
) -> LibraryServiceError:
    """
    Convenience function for handling exceptions with logging.
    
    Args:
        exception: The exception to handle
        logger: Logger instance
        operation: The operation that failed
        context: Additional context information
        user_id: User ID for audit logging
        request_id: Request ID for tracing
        
    Returns:
        Transformed Library Service exception
    """
    # Create a temporary error handler with the provided logger
    temp_handler = ErrorHandler()
    temp_handler.logger = logger
    
    transformed_exception, _ = temp_handler.handle_exception(
        exception, context, operation, user_id, request_id
    )
    
    return transformed_exception
