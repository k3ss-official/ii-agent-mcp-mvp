"""
II-Agent MCP Server Add-On - Logging Utilities
Configures and manages logging
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

# Configure logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'mcp_logs.log'
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 3

def get_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """Get a configured logger instance"""
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(LOG_FORMAT)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Create file handler
        file_path = log_file or LOG_FILE
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=LOG_MAX_SIZE,
            backupCount=LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def sanitize_log_message(message: str) -> str:
    """Sanitize log message to remove sensitive information"""
    # List of patterns to sanitize (simplified for MVP)
    patterns = [
        # API keys
        (r'key=[\w\-\.]+', 'key=***'),
        (r'Bearer [\w\-\.]+', 'Bearer ***'),
        (r'Authorization: [\w\-\.]+', 'Authorization: ***'),
        # Add more patterns as needed
    ]
    
    # Apply each pattern
    sanitized = message
    for pattern, replacement in patterns:
        sanitized = sanitized.replace(pattern, replacement)
    
    return sanitized
