"""Main application module."""

import logging
import os
import time
from typing import Any, Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.connection import connect_to_mongo, disconnect_from_mongo
from app.core.redis import connect_to_redis, disconnect_from_redis
from app.core.logging import init_logging

# Import modular system
from app.modules import register_all_modules, module_manager

# 初始化日誌系統
init_logging()

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    description="Backend API for Everly - Your Personal Diary and Travel Journal",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url=f"/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加文件大小限制中間件
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.requests import Request
from starlette import status

class LimitUploadSize(BaseHTTPMiddleware):
    def __init__(self, app, max_upload_size: int) -> None:
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next):
        if request.method == 'POST':
            if 'content-length' not in request.headers:
                logger.warning(f"請求沒有Content-Length標頭 - 路徑: {request.url.path}")
                return Response(
                    status_code=status.HTTP_411_LENGTH_REQUIRED,
                    content="沒有提供Content-Length標頭"
                )
            
            content_length = int(request.headers['content-length'])
            if content_length > self.max_upload_size:
                logger.warning(f"請求超過大小限制 - 路徑: {request.url.path}, 大小: {content_length/(1024*1024):.2f}MB, 限制: {self.max_upload_size/(1024*1024)}MB")
                return Response(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content=f"上傳文件大小不能超過{self.max_upload_size // (1024 * 1024)}MB"
                )
        
        return await call_next(request)

# 添加請求日誌中間件
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 記錄請求開始
        start_time = time.time()
        
        # 獲取請求詳情
        method = request.method
        path = request.url.path
        client = request.client.host if request.client else "unknown"
        
        # 記錄請求開始
        request_id = f"{int(time.time() * 1000)}-{os.urandom(4).hex()}"
        logger.info(f"[{request_id}] 請求開始 - {method} {path} - 客戶端: {client}")
        
        # 處理請求
        try:
            response = await call_next(request)
            
            # 計算處理時間
            process_time = (time.time() - start_time) * 1000
            status_code = response.status_code
            
            # 記錄請求結果
            logger.info(
                f"[{request_id}] 請求完成 - {method} {path} - 狀態: {status_code} - 處理時間: {process_time:.2f}ms"
            )
            
            return response
        except Exception as e:
            # 記錄請求異常
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"[{request_id}] 請求異常 - {method} {path} - 錯誤: {str(e)} - 處理時間: {process_time:.2f}ms",
                exc_info=True
            )
            raise

# 添加中間件
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(LimitUploadSize, max_upload_size=50 * 1024 * 1024)


@app.on_event("startup")
async def startup_event() -> None:
    """Execute startup tasks."""
    logger.info("Starting Everly backend...")
    
    # Ensure upload directories exist
    os.makedirs("static/uploads/profiles", exist_ok=True)
    os.makedirs("static/uploads/media", exist_ok=True)
    
    # Connect to MongoDB
    try:
        await connect_to_mongo()
        logger.info(f"成功連接到 MongoDB")
    except Exception as e:
        logger.error(f"無法連接到 MongoDB - 錯誤: {str(e)}")
        logger.error("應用程序無法啟動，因為無法連接到 MongoDB")
        raise
    
    # Connect to Redis (optional)
    try:
        await connect_to_redis()
        logger.info(f"成功連接到 Redis - 主機: {settings.REDIS_HOST}")
    except Exception as e:
        logger.warning(f"無法連接到 Redis - 錯誤: {str(e)}")
        logger.warning("應用程序將在沒有 Redis 的情況下繼續。某些功能可能會受限。")
    
    # Register and initialize all modules
    try:
        logger.info("開始註冊和初始化模塊...")
        register_all_modules()
        
        # Get database and redis connections
        from app.db.connection import get_database
        from app.core.redis import get_redis
        
        db = get_database()
        redis = get_redis()
        
        # Initialize all modules
        await module_manager.initialize_all(db, redis)
        
        # Create and include module routers
        api_router = module_manager.create_main_router()
        app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")
        
        logger.info("所有模塊註冊和初始化完成")
        
    except Exception as e:
        logger.error(f"模塊初始化失敗: {str(e)}")
        raise
    
    logger.info("Everly 後端成功啟動")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Execute shutdown tasks."""
    logger.info("正在關閉 Everly 後端...")
    
    # Cleanup all modules
    try:
        await module_manager.cleanup_all()
        logger.info("所有模塊清理完成")
    except Exception as e:
        logger.error(f"模塊清理時發生錯誤: {str(e)}")
    
    # Disconnect from Redis
    try:
        await disconnect_from_redis()
        logger.info("成功斷開與 Redis 的連接")
    except Exception as e:
        logger.warning(f"斷開與 Redis 的連接時發生錯誤: {str(e)}")
    
    # Disconnect from MongoDB
    try:
        await disconnect_from_mongo()
        logger.info("成功斷開與 MongoDB 的連接")
    except Exception as e:
        logger.error(f"斷開與 MongoDB 的連接時發生錯誤: {str(e)}")
    
    logger.info("Everly 後端關閉完成")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions."""
    path = request.url.path
    method = request.method
    
    if isinstance(exc, UnicodeDecodeError):
        logger.error(f"Unicode 解碼錯誤 - 路徑: {path}, 方法: {method}, 錯誤: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "code": "BINARY_DATA_ERROR",
                "message": "無法將二進制數據作為文本處理。請確保使用Base64編碼或適當的數據格式。"
            }
        )
    
    logger.error(f"未處理的異常 - 路徑: {path}, 方法: {method}, 錯誤類型: {type(exc).__name__}, 錯誤: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": "發生意外錯誤，請稍後再試",
        },
    )


# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root() -> Any:
    """Root endpoint."""
    return {
        "status": "success",
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.API_VERSION,
        "docs_url": "/api/docs"
    }


@app.get("/health")
async def health_check() -> Any:
    """Health check endpoint."""
    logger.debug("健康檢查請求")
    
    # Get module health status
    module_health = await module_manager.health_check_all()
    
    return {
        "status": "success",
        "message": "Healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENV,
        "modules": module_health
    }