"""Logging configuration for the application."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import List, Dict, Any

from app.core.config import settings

# Ensure the log directory exists
LOG_DIR = "app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Define log formats
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEBUG_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

# Define log file paths
MAIN_LOG_FILE = os.path.join(LOG_DIR, "app.log")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "error.log")
AUTH_LOG_FILE = os.path.join(LOG_DIR, "auth.log")

# Max log file size and backup count
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5


def get_file_handler(filename: str, level: int, format_string: str) -> RotatingFileHandler:
    """Create a rotating file log handler"""
    handler = RotatingFileHandler(
        filename=filename,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding="utf-8"
    )
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(format_string))
    return handler


def get_console_handler(level: int, format_string: str) -> logging.StreamHandler:
    """Create a console log handler"""
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(format_string))
    return handler


def setup_logging() -> None:
    """Configure application logging"""
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create handlers
    if settings.DEBUG:
        # Development environment: more verbose logging and console output
        console_handler = get_console_handler(logging.DEBUG, DEBUG_LOG_FORMAT)
        root_logger.addHandler(console_handler)
        
        file_handler = get_file_handler(MAIN_LOG_FILE, logging.DEBUG, DEBUG_LOG_FORMAT)
        root_logger.addHandler(file_handler)
    else:
        # Production environment: standard formatting, INFO level
        console_handler = get_console_handler(logging.INFO, LOG_FORMAT)
        root_logger.addHandler(console_handler)
        
        file_handler = get_file_handler(MAIN_LOG_FILE, logging.INFO, LOG_FORMAT)
        root_logger.addHandler(file_handler)
    
    # Error log - all environments
    error_handler = get_file_handler(ERROR_LOG_FILE, logging.ERROR, DEBUG_LOG_FORMAT)
    root_logger.addHandler(error_handler)
    
# Module-specific log configuration
# Authentication-related logs
    auth_logger = logging.getLogger("app.services.auth")
    auth_logger.setLevel(logging.DEBUG)
    auth_handler = get_file_handler(AUTH_LOG_FILE, logging.DEBUG, DEBUG_LOG_FORMAT)
    auth_logger.addHandler(auth_handler)
    
    auth_endpoints_logger = logging.getLogger("app.api.v1.endpoints.auth")
    auth_endpoints_logger.setLevel(logging.DEBUG)
    auth_endpoints_logger.addHandler(auth_handler)
    
# Third-party library log configuration
# httpx logs for debugging API requests
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    httpx_logger.addHandler(get_file_handler(
        os.path.join(LOG_DIR, "httpx.log"), 
        logging.DEBUG if settings.DEBUG else logging.INFO,
        DEBUG_LOG_FORMAT
    ))
    
# Disable irrelevant module logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
# Startup message
    root_logger.info(f"Logging initialized - Environment: {settings.ENV}")
    if settings.DEBUG:
        root_logger.info("Debug mode enabled - verbose logging active")

# 導出用於在應用程序開始時初始化日誌
def init_logging():
    """Initialize application logging system"""
    setup_logging() 