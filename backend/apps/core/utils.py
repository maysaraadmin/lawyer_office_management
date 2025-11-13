import uuid
import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

def generate_unique_id(prefix: str = '') -> str:
    """
    Generate a unique ID with an optional prefix.
    
    Args:
        prefix: Optional prefix for the generated ID
        
    Returns:
        str: A unique ID string
    """
    unique_id = str(uuid.uuid4())
    return f"{prefix}_{unique_id}" if prefix else unique_id

def format_date(date_obj: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object as a string.
    
    Args:
        date_obj: The datetime object to format
        fmt: The format string (default: "%Y-%m-%d %H:%M:%S")
        
    Returns:
        str: Formatted date string
    """
    if not date_obj:
        return ""
    return date_obj.strftime(fmt)

def parse_bool(value: Any) -> bool:
    """
    Safely parse a value to boolean.
    
    Args:
        value: The value to parse
        
    Returns:
        bool: The parsed boolean value
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 't', 'y', 'yes')
    return bool(value)

class APIResponse:
    """Standard API response format"""
    
    @staticmethod
    def success(
        data: Any = None, 
        message: str = "Operation completed successfully",
        status_code: int = 200
    ) -> Dict[str, Any]:
        """Create a success response"""
        return {
            'status': 'success',
            'message': message,
            'data': data,
            'status_code': status_code
        }
    
    @staticmethod
    def error(
        message: str = "An error occurred",
        errors: Optional[Dict[str, Any]] = None,
        status_code: int = 400
    ) -> Dict[str, Any]:
        """Create an error response"""
        return {
            'status': 'error',
            'message': message,
            'errors': errors or {},
            'status_code': status_code
        }


def log_exception(
    exception: Exception, 
    message: str = "An exception occurred",
    extra: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an exception with additional context.
    
    Args:
        exception: The exception that was raised
        message: Custom error message
        extra: Additional context to include in the log
    """
    extra = extra or {}
    extra['exception_type'] = type(exception).__name__
    extra['exception'] = str(exception)
    
    logger.error(message, exc_info=exception, extra=extra)
