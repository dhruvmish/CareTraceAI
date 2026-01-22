"""
Structured logging for CareTrace AI
Provides consistent logging across all agents
"""

import logging
import sys
from typing import Optional
import colorlog

def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Create a logger with colored output
    
    Args:
        name: Logger name (typically __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    if level is None:
        from src.config import LOG_LEVEL
        level = LOG_LEVEL
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create console handler with color formatting
    handler = colorlog.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    
    # Color formatter
    formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger