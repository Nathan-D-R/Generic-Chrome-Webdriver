"""
Logging Setup Utility
=====================
Configures logging for the application.
"""

import logging
import sys
from Utilities.config import Config


def setup_logging(
    log_file: str = None,
    log_level: str = None,
    include_file: bool = True,
    include_console: bool = True
):
    """
    Configure logging for the application.
    
    Args:
        log_file: Path to log file (uses Config.LOG_FILE if None)
        log_level: Logging level (uses Config.LOG_LEVEL if None)
        include_file: Whether to log to file
        include_console: Whether to log to console
    """
    log_file = log_file or Config.LOG_FILE
    log_level = log_level or Config.LOG_LEVEL
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create handlers
    handlers = []
    
    if include_console:
        console_handler = logging.StreamHandler(sys.stdout)
        handlers.append(console_handler)
    
    if include_file:
        file_handler = logging.FileHandler(log_file)
        handlers.append(file_handler)
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    logging.info(f"Logging configured: level={log_level}, file={log_file if include_file else 'None'}")
