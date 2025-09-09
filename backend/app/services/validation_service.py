"""
Validation service for handling data validation and error responses.
"""

from typing import Any, Dict, List, Optional, Type, Union
from pydantic import BaseModel, ValidationError as PydanticValidationError
from ..utils.validators import ValidationError as OldValidationError, validation_logger
from ..exceptions.base import ValidationError
from ..utils.logger import LoggerConfig


class ValidationService:
    """Service for handling data validation."""
    
    def __init__(self):
        """Initialize the validation service."""
        self.logger = LoggerConfig.get_logger("services.validation")
    
    def validate_data(
        self, 
        data: Dict[str, Any], 
        schema_class: Type[BaseModel],
        context: Optional[Dict[str, Any]] = None
    ) -> BaseModel:
        """
        Validate data against a Pydantic schema.
        
        Args:
            data: Data dictionary to validate
            schema_class: Pydantic schema class
            context: Additional context for logging
            
        Returns:
            Validated Pydantic model
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            validated_data = schema_class(**data)
            validation_logger.log_validation_success(
                schema_class.__name__, 
                str(data), 
                context
            )
            return validated_data
        except PydanticValidationError as e:
            # Convert Pydantic validation errors to our custom format
            error_messages = []
            for error in e.errors():
                field = ".".join(str(x) for x in error["loc"])
                message = error["msg"]
                value = error.get("input", "N/A")
                error_messages.append(f"{field}: {message}")
                
                # Log individual field validation errors
                validation_logger.log_validation_error(
                    OldValidationError(message, field, str(value)),
                    context
                )
            
            # Create a comprehensive error message
            error_message = f"Validation failed: {'; '.join(error_messages)}"
            validation_error = ValidationError(
                message=error_message,
                field="data",
                value=str(data),
                details={"validation_errors": error_messages}
            )
            
            # Log the overall validation failure
            validation_logger.log_validation_error(OldValidationError(error_message, "data", str(data)), context)
            raise validation_error
    
    def validate_required_fields(
        self, 
        data: Dict[str, Any], 
        required_fields: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Validate that required fields are present and not empty.
        
        Args:
            data: Data dictionary to validate
            required_fields: List of required field names
            context: Additional context for logging
            
        Raises:
            ValidationError: If required fields are missing
        """
        missing_fields = []
        
        for field in required_fields:
            if field not in data or data[field] is None or str(data[field]).strip() == "":
                missing_fields.append(field)
        
        if missing_fields:
            error_message = f"Required fields are missing: {', '.join(missing_fields)}"
            validation_error = ValidationError(
                error_message,
                field="required_fields",
                value=str(missing_fields)
            )
            
            validation_logger.log_validation_error(validation_error, context)
            raise validation_error
    
    def validate_id(self, id_value: Any, field_name: str = "id") -> int:
        """
        Validate that an ID is a positive integer.
        
        Args:
            id_value: ID value to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated integer ID
            
        Raises:
            ValidationError: If ID is invalid
        """
        try:
            id_int = int(id_value)
            if id_int <= 0:
                raise ValidationError(
                    f"{field_name} must be a positive integer",
                    field=field_name,
                    value=id_value
                )
            return id_int
        except (ValueError, TypeError):
            raise ValidationError(
                f"{field_name} must be a valid integer",
                field=field_name,
                value=id_value
            )
    
    def create_validation_error_response(
        self, 
        error: ValidationError,
        status_code: int = 400
    ) -> Dict[str, Any]:
        """
        Create a standardized error response for validation failures.
        
        Args:
            error: Validation error
            status_code: HTTP status code
            
        Returns:
            Error response dictionary
        """
        response = {
            "error": "Validation Error",
            "message": error.message,
            "field": error.field,
            "status_code": status_code
        }
        
        if error.value is not None:
            response["value"] = error.value
        
        return response
    
    def create_validation_errors_response(
        self, 
        errors: List[ValidationError],
        status_code: int = 400
    ) -> Dict[str, Any]:
        """
        Create a standardized error response for multiple validation failures.
        
        Args:
            errors: List of validation errors
            status_code: HTTP status code
            
        Returns:
            Error response dictionary
        """
        error_details = []
        for error in errors:
            error_detail = {
                "message": error.message,
                "field": error.field
            }
            if error.value is not None:
                error_detail["value"] = error.value
            error_details.append(error_detail)
        
        return {
            "error": "Validation Errors",
            "message": f"Multiple validation errors occurred ({len(errors)} errors)",
            "errors": error_details,
            "status_code": status_code
        }
    
    def log_validation_attempt(
        self, 
        operation: str, 
        data: Dict[str, Any],
        success: bool,
        error: Optional[Exception] = None
    ) -> None:
        """
        Log validation attempt for monitoring and debugging.
        
        Args:
            operation: Name of the operation being validated
            data: Data being validated
            success: Whether validation was successful
            error: Exception if validation failed
        """
        if success:
            self.logger.info(
                f"Validation successful for {operation}",
                extra={"operation": operation, "data_keys": list(data.keys())}
            )
        else:
            self.logger.warning(
                f"Validation failed for {operation}",
                extra={
                    "operation": operation,
                    "data_keys": list(data.keys()),
                    "error": str(error) if error else "Unknown error"
                }
            )


# Global validation service instance
validation_service = ValidationService()
