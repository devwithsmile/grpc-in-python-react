"""
Centralized logging configuration for the Library Service.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional


class LoggerConfig:
    """Centralized logging configuration."""
    
    # Log levels
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    
    # Default configuration
    DEFAULT_LEVEL = INFO
    DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # Log file configuration
    LOG_DIR = Path(__file__).parent.parent.parent / 'logs'
    LOG_FILE = LOG_DIR / 'library_service.log'
    ERROR_LOG_FILE = LOG_DIR / 'library_service_errors.log'
    
    # File rotation configuration
    MAX_BYTES = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT = 5
    
    @classmethod
    def setup_logging(
        cls,
        level: Optional[int] = None,
        log_to_file: bool = True,
        log_to_console: bool = True,
        service_name: str = "library_service"
    ) -> logging.Logger:
        """
        Set up centralized logging configuration.
        
        Args:
            level: Logging level (defaults to INFO)
            log_to_file: Whether to log to file
            log_to_console: Whether to log to console
            service_name: Name of the service for logger identification
            
        Returns:
            Configured logger instance
        """
        # Create logs directory if it doesn't exist
        if log_to_file:
            cls.LOG_DIR.mkdir(exist_ok=True)
        
        # Get logger
        logger = logging.getLogger(service_name)
        logger.setLevel(level or cls.DEFAULT_LEVEL)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            fmt=cls.DEFAULT_FORMAT,
            datefmt=cls.DEFAULT_DATE_FORMAT
        )
        
        simple_formatter = logging.Formatter(
            fmt='%(levelname)s - %(message)s'
        )
        
        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level or cls.DEFAULT_LEVEL)
            console_handler.setFormatter(simple_formatter)
            logger.addHandler(console_handler)
        
        # File handler for all logs
        if log_to_file:
            file_handler = logging.handlers.RotatingFileHandler(
                cls.LOG_FILE,
                maxBytes=cls.MAX_BYTES,
                backupCount=cls.BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setLevel(level or cls.DEFAULT_LEVEL)
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
            
            # Separate error log file
            error_handler = logging.handlers.RotatingFileHandler(
                cls.ERROR_LOG_FILE,
                maxBytes=cls.MAX_BYTES,
                backupCount=cls.BACKUP_COUNT,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(detailed_formatter)
            logger.addHandler(error_handler)
        
        # Prevent duplicate logs
        logger.propagate = False
        
        return logger
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger instance for a specific module.
        
        Args:
            name: Name of the module (usually __name__)
            
        Returns:
            Logger instance
        """
        return logging.getLogger(f"library_service.{name}")


def setup_exception_logging():
    """Set up global exception logging for unhandled exceptions."""
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle unhandled exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Allow KeyboardInterrupt to be handled normally
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger = logging.getLogger("library_service.exceptions")
        logger.critical(
            "Unhandled exception occurred",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    sys.excepthook = handle_exception


def log_function_call(logger: logging.Logger, func_name: str, **kwargs):
    """
    Log function call with parameters.
    
    Args:
        logger: Logger instance
        func_name: Name of the function being called
        **kwargs: Function parameters to log
    """
    params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.debug(f"Calling {func_name}({params})")


def log_function_result(logger: logging.Logger, func_name: str, result=None, **kwargs):
    """
    Log function result.
    
    Args:
        logger: Logger instance
        func_name: Name of the function
        result: Function result to log
        **kwargs: Additional context
    """
    context = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    if result is not None:
        logger.debug(f"{func_name} completed successfully. Result: {result}. Context: {context}")
    else:
        logger.debug(f"{func_name} completed successfully. Context: {context}")


def log_exception(logger: logging.Logger, message: str, exception: Exception, **kwargs):
    """
    Log an exception with stack trace and context.
    
    Args:
        logger: Logger instance
        message: Custom message for the exception
        exception: The exception that occurred
        **kwargs: Additional context
    """
    context = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.error(f"{message}. Context: {context}", exc_info=exception)


# Initialize logging on module import
def initialize_logging():
    """Initialize logging for the application."""
    # Set up logging based on environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    level = level_map.get(log_level, logging.INFO)
    log_to_file = os.getenv('LOG_TO_FILE', 'true').lower() == 'true'
    log_to_console = os.getenv('LOG_TO_CONSOLE', 'true').lower() == 'true'
    
    # Set up main logger
    main_logger = LoggerConfig.setup_logging(
        level=level,
        log_to_file=log_to_file,
        log_to_console=log_to_console
    )
    
    # Set up exception logging
    setup_exception_logging()
    
    main_logger.info("Logging system initialized")
    return main_logger


# Auto-initialize when module is imported
if __name__ != "__main__":
    initialize_logging()
