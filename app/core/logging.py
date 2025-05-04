"""Logging configuration for the application."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import List, Dict, Any

from app.core.config import settings

# 確保日誌目錄存在
LOG_DIR = "app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 定義日誌格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEBUG_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

# 定義日誌文件
MAIN_LOG_FILE = os.path.join(LOG_DIR, "app.log")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "error.log")
AUTH_LOG_FILE = os.path.join(LOG_DIR, "auth.log")

# 最大日誌文件大小和備份數量
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5


def get_file_handler(filename: str, level: int, format_string: str) -> RotatingFileHandler:
    """創建文件日誌處理器"""
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
    """創建控制台日誌處理器"""
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(format_string))
    return handler


def setup_logging() -> None:
    """設置應用程序日誌"""
    # 根日誌配置
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除現有處理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 創建處理器
    if settings.DEBUG:
        # 開發環境：更詳細的日誌和控制台輸出
        console_handler = get_console_handler(logging.DEBUG, DEBUG_LOG_FORMAT)
        root_logger.addHandler(console_handler)
        
        file_handler = get_file_handler(MAIN_LOG_FILE, logging.DEBUG, DEBUG_LOG_FORMAT)
        root_logger.addHandler(file_handler)
    else:
        # 生產環境：標準格式，INFO級別
        console_handler = get_console_handler(logging.INFO, LOG_FORMAT)
        root_logger.addHandler(console_handler)
        
        file_handler = get_file_handler(MAIN_LOG_FILE, logging.INFO, LOG_FORMAT)
        root_logger.addHandler(file_handler)
    
    # 錯誤日誌 - 所有環境
    error_handler = get_file_handler(ERROR_LOG_FILE, logging.ERROR, DEBUG_LOG_FORMAT)
    root_logger.addHandler(error_handler)
    
    # 特定模塊的日誌配置
    # 認證相關日誌
    auth_logger = logging.getLogger("app.services.auth")
    auth_logger.setLevel(logging.DEBUG)
    auth_handler = get_file_handler(AUTH_LOG_FILE, logging.DEBUG, DEBUG_LOG_FORMAT)
    auth_logger.addHandler(auth_handler)
    
    auth_endpoints_logger = logging.getLogger("app.api.v1.endpoints.auth")
    auth_endpoints_logger.setLevel(logging.DEBUG)
    auth_endpoints_logger.addHandler(auth_handler)
    
    # 第三方庫日誌配置
    # httpx日誌，用於調試API請求
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    httpx_logger.addHandler(get_file_handler(
        os.path.join(LOG_DIR, "httpx.log"), 
        logging.DEBUG if settings.DEBUG else logging.INFO,
        DEBUG_LOG_FORMAT
    ))
    
    # 禁用其他不相關的模塊日誌
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # 啟動消息
    root_logger.info(f"Logging initialized - Environment: {settings.ENV}")
    if settings.DEBUG:
        root_logger.info("Debug mode enabled - verbose logging active")

# 導出用於在應用程序開始時初始化日誌
def init_logging():
    """初始化應用程序日誌系統"""
    setup_logging() 