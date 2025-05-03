"""Main application module."""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.core.config import settings
from app.db.connection import connect_to_mongo, disconnect_from_mongo
from app.core.redis import connect_to_redis, disconnect_from_redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
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


@app.on_event("startup")
async def startup_event() -> None:
    """Execute startup tasks."""
    logger.info("Starting Everly backend...")
    
    # Connect to MongoDB
    try:
        await connect_to_mongo()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        logger.error("Application cannot start without MongoDB")
        raise
    
    # Connect to Redis (optional)
    try:
        await connect_to_redis()
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}")
        logger.warning("Application will continue without Redis. Some features may be limited.")
    
    logger.info("Everly backend started successfully")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Execute shutdown tasks."""
    logger.info("Shutting down Everly backend...")
    
    # Disconnect from Redis
    try:
        await disconnect_from_redis()
    except Exception as e:
        logger.warning(f"Error while disconnecting from Redis: {e}")
    
    # Disconnect from MongoDB
    try:
        await disconnect_from_mongo()
    except Exception as e:
        logger.error(f"Error while disconnecting from MongoDB: {e}")
    
    logger.info("Everly backend shutdown complete")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
        },
    )


# Include API router
app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")


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
    return {
        "status": "success",
        "message": "Healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENV
    } 