import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
LOG_LEVEL = logging.INFO

def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """
    Set up a logger with both file and console handlers
    
    Args:
        name: Logger name (usually __name__)
        log_file: Optional specific log file name
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(LOG_LEVEL)
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        file_path = logs_dir / log_file
    else:
        # Use module name for file
        module_name = name.split('.')[-1] if '.' in name else name
        file_path = logs_dir / f"{module_name}.log"
    
    # Rotating file handler (10MB max, keep 5 backup files)
    file_handler = logging.handlers.RotatingFileHandler(
        file_path,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error file handler (separate file for errors)
    error_file_path = logs_dir / f"{file_path.stem}_errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_file_path,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Logger instance
    """
    return setup_logger(name)

# Create main application logger
app_logger = get_logger('hirevision')

def log_function_call(func):
    """
    Decorator to log function calls with parameters and return values
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        func_name = func.__name__
        
        # Log function entry
        logger.info(f"Entering function: {func_name}")
        
        # Log parameters (sanitized)
        if args:
            logger.debug(f"Function {func_name} called with args: {str(args)[:200]}...")
        if kwargs:
            # Filter out sensitive data
            safe_kwargs = {k: v for k, v in kwargs.items() 
                          if k.lower() not in ['password', 'api_key', 'token', 'secret']}
            logger.debug(f"Function {func_name} called with kwargs: {safe_kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.info(f"Function {func_name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Function {func_name} failed with error: {str(e)}", exc_info=True)
            raise
    
    return wrapper

def log_api_call(api_name: str, request_data: dict = None, response_data: dict = None, 
                 success: bool = True, error: str = None):
    """
    Log API calls with request and response data
    
    Args:
        api_name: Name of the API being called
        request_data: Request data (will be sanitized)
        response_data: Response data
        success: Whether the API call was successful
        error: Error message if the call failed
    """
    logger = get_logger('api_calls')
    
    # Sanitize sensitive data
    if request_data:
        safe_request = {k: v for k, v in request_data.items() 
                       if k.lower() not in ['password', 'api_key', 'token', 'secret']}
    else:
        safe_request = None
    
    if success:
        logger.info(f"API call to {api_name} successful")
        if safe_request:
            logger.debug(f"Request data: {safe_request}")
        if response_data:
            logger.debug(f"Response data: {str(response_data)[:500]}...")
    else:
        logger.error(f"API call to {api_name} failed: {error}")
        if safe_request:
            logger.debug(f"Request data: {safe_request}")

def log_user_action(user_id: str, action: str, details: str = None, success: bool = True):
    """
    Log user actions for audit trail
    
    Args:
        user_id: User identifier
        action: Action performed
        details: Additional details about the action
        success: Whether the action was successful
    """
    logger = get_logger('user_actions')
    
    if success:
        logger.info(f"User {user_id} performed action: {action}")
        if details:
            logger.debug(f"Action details: {details}")
    else:
        logger.warning(f"User {user_id} failed to perform action: {action}")
        if details:
            logger.debug(f"Failure details: {details}")

def log_file_operation(operation: str, file_path: str, success: bool = True, 
                      file_size: int = None, error: str = None):
    """
    Log file operations
    
    Args:
        operation: Type of operation (upload, download, delete, etc.)
        file_path: Path to the file
        success: Whether the operation was successful
        file_size: Size of the file in bytes
        error: Error message if the operation failed
    """
    logger = get_logger('file_operations')
    
    if success:
        logger.info(f"File operation '{operation}' successful for: {file_path}")
        if file_size:
            logger.debug(f"File size: {file_size} bytes")
    else:
        logger.error(f"File operation '{operation}' failed for: {file_path}")
        if error:
            logger.error(f"Error: {error}")

def log_performance(operation: str, duration: float, details: str = None):
    """
    Log performance metrics
    
    Args:
        operation: Name of the operation
        duration: Duration in seconds
        details: Additional performance details
    """
    logger = get_logger('performance')
    
    logger.info(f"Performance - {operation}: {duration:.3f}s")
    if details:
        logger.debug(f"Performance details: {details}")

# Initialize main loggers
resume_analyzer_logger = get_logger('resume_analyzer')
learning_path_logger = get_logger('learning_path_analyzer')
resume_builder_logger = get_logger('resume_builder')
pdf_generator_logger = get_logger('pdf_generator')
utils_logger = get_logger('utils')
views_logger = get_logger('views')
tasks_logger = get_logger('tasks')
models_logger = get_logger('models') 