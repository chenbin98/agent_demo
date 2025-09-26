"""Logging configuration for the agent demo."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    verbose: bool = False
) -> logging.Logger:
    """Set up logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        verbose: Enable verbose output to stderr
    
    Returns:
        Configured logger instance
    """
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger("agent_demo")
    logger.setLevel(numeric_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (stderr)
    if verbose or level.upper() == "DEBUG":
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "agent_demo") -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggingContext:
    """Context manager for temporary logging configuration."""
    
    def __init__(self, level: str = "DEBUG", log_file: Optional[str] = None):
        self.level = level
        self.log_file = log_file
        self.original_handlers = []
        self.original_level = None
    
    def __enter__(self):
        logger = logging.getLogger("agent_demo")
        self.original_level = logger.level
        self.original_handlers = logger.handlers.copy()
        
        logger.handlers.clear()
        setup_logging(self.level, self.log_file, verbose=True)
        
        return logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logger = logging.getLogger("agent_demo")
        logger.handlers.clear()
        logger.setLevel(self.original_level)
        logger.handlers.extend(self.original_handlers)


def log_function_call(func_name: str, args: dict, result: str = None):
    """Log function calls for debugging.
    
    Args:
        func_name: Name of the function being called
        args: Function arguments
        result: Function result (optional)
    """
    logger = get_logger()
    
    logger.debug(f"Calling {func_name} with args: {args}")
    if result:
        logger.debug(f"{func_name} returned: {result[:200]}..." if len(result) > 200 else f"{func_name} returned: {result}")


def log_error(error: Exception, context: str = ""):
    """Log errors with context.
    
    Args:
        error: Exception instance
        context: Additional context information
    """
    logger = get_logger()
    
    if context:
        logger.error(f"Error in {context}: {error}")
    else:
        logger.error(f"Error: {error}")
    
    logger.debug(f"Error details: {error}", exc_info=True)