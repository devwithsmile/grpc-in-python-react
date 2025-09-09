"""
Base service class with common functionality for all services.
"""

from typing import Any, Dict, Optional, Type, TypeVar
from sqlalchemy.orm import Session
from ..infrastructure.database import get_db_session, DatabaseError
from ..utils.logger import LoggerConfig, log_function_call, log_function_result
from ..exceptions.base import ValidationError, LibraryServiceError
from ..exceptions.error_handler import error_handler

T = TypeVar('T')


class BaseService:
    """Base service class with common functionality."""
    
    def __init__(self, service_name: str):
        """Initialize the service with logger."""
        self.logger = LoggerConfig.get_logger(f"services.{service_name}")
        self.service_name = service_name
    
    def _handle_validation_error(
        self, 
        error: ValidationError, 
        operation: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Handle validation errors with structured logging."""
        error_handler.handle_exception(
            error,
            context=context,
            operation=operation
        )
        raise error
    
    def _handle_database_error(
        self, 
        error: DatabaseError, 
        operation: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Handle database errors with structured logging."""
        error_handler.handle_exception(
            error,
            context=context,
            operation=operation
        )
        raise error
    
    def _handle_generic_error(
        self, 
        error: Exception, 
        operation: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Handle generic errors with structured logging."""
        error_handler.handle_exception(
            error,
            context=context,
            operation=operation
        )
        raise error
    
    def _execute_with_error_handling(
        self,
        operation: str,
        func,
        *args,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """Execute a function with comprehensive error handling."""
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            self._handle_validation_error(e, operation, context)
        except DatabaseError as e:
            self._handle_database_error(e, operation, context)
        except Exception as e:
            self._handle_generic_error(e, operation, context)
    
    def _log_function_call(self, func_name: str, **kwargs) -> None:
        """Log function call with context."""
        log_function_call(self.logger, func_name, **kwargs)
    
    def _log_function_result(self, func_name: str, result: str, **kwargs) -> None:
        """Log function result with context."""
        log_function_result(self.logger, func_name, result, **kwargs)
    
    def _get_by_id(
        self, 
        model_class: Type[T], 
        id_value: int, 
        operation: str,
        not_found_error_class: Type[LibraryServiceError],
        context: Optional[Dict[str, Any]] = None
    ) -> T:
        """Get a record by ID with error handling."""
        self._log_function_call(operation, id=id_value)
        
        try:
            with get_db_session() as session:
                record = session.query(model_class).filter(model_class.id == id_value).first()
                if not record:
                    error = not_found_error_class(id_value, context)
                    self._handle_generic_error(error, operation, context)
                
                self._log_function_result(operation, f"Found {model_class.__name__}: {record.id}", id=id_value)
                return record
        except DatabaseError as e:
            self._handle_database_error(e, operation, context)
        except Exception as e:
            self._handle_generic_error(e, operation, context)
    
    def _get_all(
        self, 
        model_class: Type[T], 
        operation: str,
        context: Optional[Dict[str, Any]] = None
    ) -> list[T]:
        """Get all records with error handling."""
        self._log_function_call(operation)
        
        try:
            with get_db_session() as session:
                records = session.query(model_class).all()
                self._log_function_result(operation, f"Found {len(records)} {model_class.__name__} records")
                return records
        except DatabaseError as e:
            self._handle_database_error(e, operation, context)
        except Exception as e:
            self._handle_generic_error(e, operation, context)
    
    def _create_record(
        self, 
        model_class: Type[T], 
        operation: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> T:
        """Create a new record with error handling."""
        self._log_function_call(operation, **kwargs)
        
        try:
            with get_db_session() as session:
                record = model_class(**kwargs)
                session.add(record)
                session.flush()  # Get the ID without committing
                session.refresh(record)
                self._log_function_result(operation, f"{model_class.__name__} created with ID {record.id}", id=record.id)
                return record
        except DatabaseError as e:
            self._handle_database_error(e, operation, context)
        except Exception as e:
            self._handle_generic_error(e, operation, context)
    
    def _update_record(
        self, 
        model_class: Type[T], 
        id_value: int, 
        operation: str,
        not_found_error_class: Type[LibraryServiceError],
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> T:
        """Update a record with error handling."""
        self._log_function_call(operation, id=id_value, **kwargs)
        
        try:
            with get_db_session() as session:
                record = session.query(model_class).filter(model_class.id == id_value).first()
                if not record:
                    error = not_found_error_class(id_value, context)
                    self._handle_generic_error(error, operation, context)
                
                # Update fields
                for key, value in kwargs.items():
                    if hasattr(record, key) and value is not None:
                        setattr(record, key, value)
                
                session.flush()
                session.refresh(record)
                self._log_function_result(operation, f"{model_class.__name__} updated with ID {record.id}", id=record.id)
                return record
        except DatabaseError as e:
            self._handle_database_error(e, operation, context)
        except Exception as e:
            self._handle_generic_error(e, operation, context)
    
    def _delete_record(
        self, 
        model_class: Type[T], 
        id_value: int, 
        operation: str,
        not_found_error_class: Type[LibraryServiceError],
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Delete a record with error handling."""
        self._log_function_call(operation, id=id_value)
        
        try:
            with get_db_session() as session:
                record = session.query(model_class).filter(model_class.id == id_value).first()
                if not record:
                    error = not_found_error_class(id_value, context)
                    self._handle_generic_error(error, operation, context)
                
                session.delete(record)
                self._log_function_result(operation, f"{model_class.__name__} deleted with ID {id_value}", id=id_value)
                return True
        except DatabaseError as e:
            self._handle_database_error(e, operation, context)
        except Exception as e:
            self._handle_generic_error(e, operation, context)
