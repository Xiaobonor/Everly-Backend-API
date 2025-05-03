"""Redis connection module."""

import logging
from typing import Dict, Optional

import redis.asyncio as aioredis
from redis.asyncio.client import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis connection instance
redis_client: Optional[Redis] = None


async def get_redis() -> Optional[Redis]:
    """
    Get the Redis client instance.
    
    This function returns the Redis client instance.
    It is designed to be used as a FastAPI dependency.
    Returns None if Redis is not connected.
    """
    return redis_client


async def connect_to_redis() -> None:
    """
    Connect to Redis using settings from the config.
    
    This function establishes a connection to Redis using the host,
    port and password specified in the application settings.
    If connection fails, it logs the error but allows the application to continue.
    """
    global redis_client
    try:
        logger.info("Connecting to Redis...")
        
        # 构建 Redis URL，并添加密码认证
        redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
        connection_kwargs: Dict[str, any] = {
            "encoding": "utf-8",
            "decode_responses": True
        }
        
        # 如果有密码，则添加密码认证
        if settings.REDIS_PASSWORD:
            connection_kwargs["password"] = settings.REDIS_PASSWORD
            logger.info("Redis password authentication enabled")
        
        redis_client = aioredis.from_url(
            redis_url,
            **connection_kwargs
        )
        
        await redis_client.ping()
        logger.info("Connected to Redis successfully.")
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}")
        logger.warning("Application will continue without Redis. Some features may be limited.")
        redis_client = None


async def disconnect_from_redis() -> None:
    """
    Disconnect from Redis.
    
    This function closes the connection to Redis.
    """
    global redis_client
    if redis_client:
        try:
            logger.info("Disconnecting from Redis...")
            await redis_client.close()
            redis_client = None
            logger.info("Disconnected from Redis successfully.")
        except Exception as e:
            logger.error(f"Error while disconnecting from Redis: {e}")
            redis_client = None